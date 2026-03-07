import unittest
import tempfile
import os
import shutil
from pathlib import Path

import myclaw.config

class TestConfigCache(unittest.TestCase):
    def setUp(self):
        # Isolate the test environment using a temporary directory as stated in memory.
        self.test_dir = tempfile.mkdtemp()
        self.test_dir_path = Path(self.test_dir)

        # Save original config paths
        self.original_config_dir = myclaw.config.CONFIG_DIR
        self.original_config_file = myclaw.config.CONFIG_FILE
        self.original_workspace = myclaw.config.WORKSPACE
        self.original_cache = myclaw.config._CONFIG_CACHE
        self.original_mtime = myclaw.config._CONFIG_MTIME

        # Override with test paths
        myclaw.config.CONFIG_DIR = self.test_dir_path
        myclaw.config.CONFIG_FILE = self.test_dir_path / "config.json"
        myclaw.config.WORKSPACE = self.test_dir_path / "workspace"
        myclaw.config._CONFIG_CACHE = None
        myclaw.config._CONFIG_MTIME = 0.0

    def tearDown(self):
        # Restore original paths
        myclaw.config.CONFIG_DIR = self.original_config_dir
        myclaw.config.CONFIG_FILE = self.original_config_file
        myclaw.config.WORKSPACE = self.original_workspace
        myclaw.config._CONFIG_CACHE = self.original_cache
        myclaw.config._CONFIG_MTIME = self.original_mtime

        # Clean up temporary directory
        shutil.rmtree(self.test_dir)

    def test_load_config_detects_external_changes(self):
        """Test that load_config reads from disk again when the mtime changes."""
        import time
        # Write initial config
        initial_config = {"key": "value"}
        myclaw.config.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        myclaw.config.CONFIG_FILE.write_text('{"key": "value"}')

        # Load config
        config1 = myclaw.config.load_config()
        self.assertEqual(config1, initial_config)

        # Ensure mtime updates by sleeping slightly (or artificially modifying mtime)
        time.sleep(0.01)

        # Modify file directly to bypass save_config
        myclaw.config.CONFIG_FILE.write_text('{"key": "new_value"}')

        # Load config again - should detect new mtime and reload
        config2 = myclaw.config.load_config()
        self.assertEqual(config2, {"key": "new_value"})
        self.assertEqual(myclaw.config._CONFIG_CACHE, {"key": "new_value"})

    def test_load_config_caches_result(self):
        """Test that load_config uses cache when mtime hasn't changed."""
        import unittest.mock
        # Write initial config
        initial_config = {"key": "value"}
        myclaw.config.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        myclaw.config.CONFIG_FILE.write_text('{"key": "value"}')

        config1 = myclaw.config.load_config()
        self.assertEqual(config1, initial_config)

        # Mock json.loads to ensure it's not called again
        with unittest.mock.patch('json.loads') as mock_json_loads:
            config2 = myclaw.config.load_config()
            self.assertEqual(config2, initial_config)
            mock_json_loads.assert_not_called()

    def test_cache_poisoning_prevention(self):
        """Test that modifying the returned config does not alter the cache."""
        myclaw.config.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        myclaw.config.CONFIG_FILE.write_text('{"key": "value", "nested": {"a": 1}}')

        config1 = myclaw.config.load_config()

        # Mutate the returned config
        config1["key"] = "mutated"
        config1["nested"]["a"] = 99

        # Load again - should be unaffected by the mutation
        config2 = myclaw.config.load_config()
        self.assertEqual(config2["key"], "value")
        self.assertEqual(config2["nested"]["a"], 1)

    def test_save_config_updates_cache(self):
        """Test that save_config updates both the cache and the file."""
        new_config = {"new_key": "new_value"}
        myclaw.config.save_config(new_config)

        # Cache should be updated
        self.assertEqual(myclaw.config._CONFIG_CACHE, new_config)

        # Mutate to ensure cache wasn't just a reference
        new_config["new_key"] = "mutated"
        self.assertEqual(myclaw.config._CONFIG_CACHE["new_key"], "new_value")

        # File should be updated (read directly to verify)
        import json
        file_content = json.loads(myclaw.config.CONFIG_FILE.read_text())
        self.assertEqual(file_content, {"new_key": "new_value"})

if __name__ == '__main__':
    unittest.main()
