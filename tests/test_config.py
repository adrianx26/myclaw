import unittest
import tempfile
import shutil
import time
import json
from pathlib import Path

# Note: tests are run using standard unittest.
import myclaw.config as config

class TestConfig(unittest.TestCase):
    def setUp(self):
        # Isolate the test environment using tempfile
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

        # Override the global paths in the config module
        self.original_config_dir = config.CONFIG_DIR
        self.original_config_file = config.CONFIG_FILE
        self.original_workspace = config.WORKSPACE

        config.CONFIG_DIR = self.test_path / ".myclaw"
        config.CONFIG_FILE = config.CONFIG_DIR / "config.json"
        config.WORKSPACE = config.CONFIG_DIR / "workspace"

        # Reset globals before each test
        config._CONFIG_CACHE = None
        config._CONFIG_MTIME = 0.0

    def tearDown(self):
        # Restore globals
        config.CONFIG_DIR = self.original_config_dir
        config.CONFIG_FILE = self.original_config_file
        config.WORKSPACE = self.original_workspace

        # Clean up temporary directory
        shutil.rmtree(self.test_dir)

    def test_load_config_no_file(self):
        # Should return {} and clear cache when file does not exist
        result = config.load_config()
        self.assertEqual(result, {})
        self.assertEqual(config._CONFIG_CACHE, {})

    def test_save_and_load_config_cache(self):
        test_config = {"token": "123", "user_id": 456}

        # Save config, which should update cache and mtime
        config.save_config(test_config)

        # Load config, should hit cache
        result = config.load_config()

        # Ensure values match
        self.assertEqual(result, test_config)

        # Ensure deepcopy protection is working
        result["token"] = "changed"
        self.assertNotEqual(config._CONFIG_CACHE["token"], "changed")

    def test_mtime_invalidation(self):
        test_config = {"token": "123"}
        config.save_config(test_config)

        # Load once to cache
        config.load_config()

        # Simulate external modification: sleep slightly so mtime actually changes
        time.sleep(0.01)
        new_config = {"token": "999"}
        config.CONFIG_FILE.write_text(json.dumps(new_config))

        # Next load_config should detect mtime change and update cache
        result = config.load_config()
        self.assertEqual(result, new_config)
        self.assertEqual(config._CONFIG_CACHE, new_config)
