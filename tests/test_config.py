import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
import copy

import myclaw.config as config

class TestConfig(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to act as the config dir
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Override the global paths in config module
        self.original_config_dir = config.CONFIG_DIR
        self.original_config_file = config.CONFIG_FILE
        self.original_workspace = config.WORKSPACE

        config.CONFIG_DIR = self.temp_path
        config.CONFIG_FILE = self.temp_path / "config.json"
        config.WORKSPACE = self.temp_path / "workspace"

        # Reset cache
        self.original_cache = config._CONFIG_CACHE
        self.original_mtime = config._CONFIG_MTIME
        config._CONFIG_CACHE = None
        config._CONFIG_MTIME = 0.0

    def tearDown(self):
        # Restore original paths and cache
        config.CONFIG_DIR = self.original_config_dir
        config.CONFIG_FILE = self.original_config_file
        config.WORKSPACE = self.original_workspace
        config._CONFIG_CACHE = self.original_cache
        config._CONFIG_MTIME = self.original_mtime
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_load_config_missing_file(self):
        result = config.load_config()
        self.assertEqual(result, {})
        self.assertEqual(config._CONFIG_CACHE, {})
        self.assertEqual(config._CONFIG_MTIME, 0.0)

    def test_save_and_load_config(self):
        test_data = {"key": "value"}
        config.save_config(test_data)

        self.assertTrue(config.CONFIG_FILE.exists())
        self.assertEqual(json.loads(config.CONFIG_FILE.read_text()), test_data)
        self.assertEqual(config._CONFIG_CACHE, test_data)

        # Ensure deep copy is returned by load_config
        loaded_data = config.load_config()
        self.assertEqual(loaded_data, test_data)

        # Modify loaded data and verify cache is not affected
        loaded_data["key"] = "new_value"
        self.assertEqual(config._CONFIG_CACHE, test_data)

    def test_save_config_deep_copy(self):
        test_data = {"nested": {"key": "value"}}
        config.save_config(test_data)

        # Modify the original data passed to save_config
        test_data["nested"]["key"] = "new_value"

        # Verify the cache wasn't affected
        self.assertEqual(config._CONFIG_CACHE, {"nested": {"key": "value"}})

    def test_load_config_mtime_cache(self):
        test_data = {"key": "value"}
        config.save_config(test_data)

        # First load should hit the cache we just set in save_config
        with patch.object(Path, 'read_text') as mock_read_text:
            result = config.load_config()
            self.assertEqual(result, test_data)
            mock_read_text.assert_not_called()

        import time
        time.sleep(0.01) # to ensure mtime changes
        # Simulate an external change to the file
        new_data = {"key": "new_value"}
        config.CONFIG_FILE.write_text(json.dumps(new_data))

        # Next load should notice the mtime change and read from file
        result = config.load_config()
        self.assertEqual(result, new_data)
        self.assertEqual(config._CONFIG_CACHE, new_data)

if __name__ == '__main__':
    unittest.main()
