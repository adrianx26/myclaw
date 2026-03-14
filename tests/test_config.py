import unittest
import tempfile
import shutil
from pathlib import Path
import json
import copy
from unittest.mock import patch, MagicMock

import myclaw.config as config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.test_dir) / ".myclaw"
        self.config_file = self.config_dir / "config.json"
        self.workspace = self.config_dir / "workspace"

        # Override module variables
        self.orig_config_dir = config.CONFIG_DIR
        self.orig_config_file = config.CONFIG_FILE
        self.orig_workspace = config.WORKSPACE

        config.CONFIG_DIR = self.config_dir
        config.CONFIG_FILE = self.config_file
        config.WORKSPACE = self.workspace

        # Reset cache for tests
        config._CONFIG_CACHE = None
        config._CONFIG_MTIME = 0

    def tearDown(self):
        # Restore module variables
        config.CONFIG_DIR = self.orig_config_dir
        config.CONFIG_FILE = self.orig_config_file
        config.WORKSPACE = self.orig_workspace

        # Clean up temp dir
        shutil.rmtree(self.test_dir)

    def test_load_save_config_with_cache(self):
        # 1. First load: file doesn't exist, should return {}
        data = config.load_config()
        self.assertEqual(data, {})
        self.assertTrue(self.config_dir.exists())
        self.assertTrue(self.workspace.exists())

        # 2. Save config: should write to disk and update cache
        test_data = {"token": "123", "user_id": 456}
        config.save_config(test_data)

        # Verify file contents
        file_data = json.loads(self.config_file.read_text())
        self.assertEqual(file_data, test_data)

        # Verify it deepcopies
        test_data["token"] = "789"

        # 3. Load config: should hit cache and not read file again
        with patch('myclaw.config.Path.read_text', wraps=self.config_file.read_text) as mock_read:
            loaded_data = config.load_config()
            self.assertEqual(loaded_data, {"token": "123", "user_id": 456})
            mock_read.assert_not_called()

        # 4. Modify loaded data: should not affect cache
        loaded_data["token"] = "abc"
        loaded_data2 = config.load_config()
        self.assertEqual(loaded_data2, {"token": "123", "user_id": 456})

    def test_load_config_clears_cache_if_file_deleted(self):
        # Setup initial cached state
        test_data = {"token": "123", "user_id": 456}
        config.save_config(test_data)

        # Verify it loads correctly
        self.assertEqual(config.load_config(), test_data)

        # Delete the file
        self.config_file.unlink()

        # Load again: should hit FileNotFoundError, clear cache, and return {}
        self.assertEqual(config.load_config(), {})
        self.assertEqual(config._CONFIG_CACHE, {})
        self.assertEqual(config._CONFIG_MTIME, 0.0)

    def test_save_config_updates_after_write(self):
        # Verify that if write fails, cache is not updated
        config._CONFIG_CACHE = {"old": "data"}

        with patch('myclaw.config.Path.write_text', side_effect=Exception("Disk error")):
            with self.assertRaises(Exception):
                config.save_config({"new": "data"})

        self.assertEqual(config._CONFIG_CACHE, {"old": "data"})

if __name__ == '__main__':
    unittest.main()