import unittest
import tempfile
import shutil
import time
import json
from pathlib import Path
import myclaw.config as config
from myclaw.config import load_config, save_config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.orig_config_dir = config.CONFIG_DIR
        self.orig_config_file = config.CONFIG_FILE
        self.orig_workspace = config.WORKSPACE

        config.CONFIG_DIR = self.temp_dir
        config.CONFIG_FILE = self.temp_dir / "config.json"
        config.WORKSPACE = self.temp_dir / "workspace"

        config._CONFIG_CACHE = None
        config._LAST_MTIME = None

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        config.CONFIG_DIR = self.orig_config_dir
        config.CONFIG_FILE = self.orig_config_file
        config.WORKSPACE = self.orig_workspace
        config._CONFIG_CACHE = None
        config._LAST_MTIME = None

    def test_load_save_config(self):
        # Should return empty dict initially
        self.assertEqual(load_config(), {})

        # Save config
        save_config({"foo": "bar"})
        self.assertEqual(load_config(), {"foo": "bar"})

        # Modify externally
        time.sleep(0.01) # Small delay for mtime precision
        config.CONFIG_FILE.write_text(json.dumps({"foo": "baz"}))
        self.assertEqual(load_config(), {"foo": "baz"})

if __name__ == '__main__':
    unittest.main()
