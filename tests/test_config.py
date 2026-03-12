import unittest
import tempfile
import shutil
import os
import json
from pathlib import Path
import time
import copy

import myclaw.config as config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Override global paths in config
        self.orig_config_dir = config.CONFIG_DIR
        self.orig_config_file = config.CONFIG_FILE
        self.orig_workspace = config.WORKSPACE

        config.CONFIG_DIR = self.temp_path / ".myclaw"
        config.CONFIG_FILE = config.CONFIG_DIR / "config.json"
        config.WORKSPACE = config.CONFIG_DIR / "workspace"

        # Reset cache
        config._CONFIG_CACHE = None
        config._LAST_MTIME = 0.0

    def tearDown(self):
        # Restore globals
        config.CONFIG_DIR = self.orig_config_dir
        config.CONFIG_FILE = self.orig_config_file
        config.WORKSPACE = self.orig_workspace

        shutil.rmtree(self.temp_dir)

    def test_load_config_empty(self):
        c = config.load_config()
        self.assertEqual(c, {})
        self.assertTrue(config.CONFIG_DIR.exists())
        self.assertTrue(config.WORKSPACE.exists())

    def test_save_and_load(self):
        data = {"test_key": "test_value", "nested": {"foo": "bar"}}
        config.save_config(data)

        c = config.load_config()
        self.assertEqual(c, data)
        self.assertEqual(config._CONFIG_CACHE, data)

    def test_cache_hit(self):
        data = {"count": 1}
        config.save_config(data)

        # Load to prime cache
        c1 = config.load_config()

        # Directly modify file without updating mtime
        # In real life mtime would update, but this tests that if mtime is same, cache is used.
        # However, to test this, we can just modify the file content without changing mtime.
        current_mtime = config.CONFIG_FILE.stat().st_mtime

        with open(config.CONFIG_FILE, 'w') as f:
            f.write('{"count": 2}')

        # Restore original mtime so it looks untouched
        os.utime(config.CONFIG_FILE, (current_mtime, current_mtime))

        c2 = config.load_config()
        # Should still be 1 because mtime hasn't changed
        self.assertEqual(c2["count"], 1)

    def test_cache_miss_on_mtime_change(self):
        data = {"count": 1}
        config.save_config(data)

        # Load to prime cache
        c1 = config.load_config()
        self.assertEqual(c1["count"], 1)

        # Wait a tiny bit and modify file to update mtime
        time.sleep(0.01)
        with open(config.CONFIG_FILE, 'w') as f:
            f.write('{"count": 2}')

        c2 = config.load_config()
        # Should be 2 because mtime changed
        self.assertEqual(c2["count"], 2)

    def test_deepcopy_protection_load(self):
        data = {"items": [1, 2, 3]}
        config.save_config(data)

        c1 = config.load_config()
        c1["items"].append(4)

        c2 = config.load_config()
        self.assertEqual(c2["items"], [1, 2, 3])
        self.assertEqual(config._CONFIG_CACHE["items"], [1, 2, 3])

    def test_deepcopy_protection_save(self):
        data = {"items": [1, 2, 3]}
        config.save_config(data)

        # Mutate the original data dict
        data["items"].append(4)

        # Check cache wasn't mutated
        c1 = config.load_config()
        self.assertEqual(c1["items"], [1, 2, 3])

if __name__ == '__main__':
    unittest.main()
