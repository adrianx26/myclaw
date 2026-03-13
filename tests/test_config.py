import unittest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import patch

import myclaw.config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.test_dir) / ".myclaw"
        self.config_file = self.config_dir / "config.json"
        self.workspace = self.config_dir / "workspace"

        # Patch the paths in myclaw.config
        self.patcher1 = patch('myclaw.config.CONFIG_DIR', self.config_dir)
        self.patcher2 = patch('myclaw.config.CONFIG_FILE', self.config_file)
        self.patcher3 = patch('myclaw.config.WORKSPACE', self.workspace)

        self.patcher1.start()
        self.patcher2.start()
        self.patcher3.start()

        # Reset cache for clean state
        myclaw.config._CONFIG_CACHE = None
        myclaw.config._CONFIG_MTIME = 0.0

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()
        shutil.rmtree(self.test_dir)

    def test_load_config_no_file(self):
        config = myclaw.config.load_config()
        self.assertEqual(config, {})
        self.assertTrue(self.config_dir.exists())
        self.assertTrue(self.workspace.exists())

    def test_load_config_with_file(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(json.dumps({"test": "value"}))

        config = myclaw.config.load_config()
        self.assertEqual(config, {"test": "value"})

    def test_save_config(self):
        myclaw.config.save_config({"new": "data"})

        self.assertTrue(self.config_file.exists())
        data = json.loads(self.config_file.read_text())
        self.assertEqual(data, {"new": "data"})

        # Test cache desync protection
        self.assertEqual(myclaw.config._CONFIG_CACHE, {"new": "data"})

    def test_caching(self):
        # 1. Save config
        myclaw.config.save_config({"key": "val1"})

        # 2. Load it
        config1 = myclaw.config.load_config()
        self.assertEqual(config1, {"key": "val1"})

        # 3. Change file behind the scenes and update mtime
        self.config_file.write_text(json.dumps({"key": "val2"}))
        new_mtime = self.config_file.stat().st_mtime + 1.0
        os.utime(self.config_file, (new_mtime, new_mtime))

        # 4. Load again, should load new because mtime changed
        config2 = myclaw.config.load_config()
        self.assertEqual(config2, {"key": "val2"})

        # 5. Mutate returned dict, should not affect cache (deepcopy)
        config2["key"] = "mutated"
        config3 = myclaw.config.load_config()
        self.assertEqual(config3, {"key": "val2"})

    def test_save_config_mutation(self):
        # Save config
        cfg = {"key": "val"}
        myclaw.config.save_config(cfg)

        # Mutate the input dict
        cfg["key"] = "mutated"

        # Cache should not be mutated
        config = myclaw.config.load_config()
        self.assertEqual(config, {"key": "val"})

if __name__ == "__main__":
    unittest.main()
