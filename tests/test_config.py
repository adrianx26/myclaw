import unittest
import tempfile
import shutil
import time
from pathlib import Path
from unittest.mock import patch
import myclaw.config as config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.test_dir) / ".myclaw"
        self.config_file = self.config_dir / "config.json"
        self.workspace = self.config_dir / "workspace"

        # Override paths
        self.patcher_dir = patch('myclaw.config.CONFIG_DIR', self.config_dir)
        self.patcher_file = patch('myclaw.config.CONFIG_FILE', self.config_file)
        self.patcher_workspace = patch('myclaw.config.WORKSPACE', self.workspace)

        self.patcher_dir.start()
        self.patcher_file.start()
        self.patcher_workspace.start()

        # Reset cache
        config._CONFIG_CACHE = None
        config._CONFIG_MTIME = 0.0

    def tearDown(self):
        self.patcher_dir.stop()
        self.patcher_file.stop()
        self.patcher_workspace.stop()
        shutil.rmtree(self.test_dir)

    def test_load_config_empty(self):
        # Should return empty dict when no file exists
        conf = config.load_config()
        self.assertEqual(conf, {})

        # Directories should be created
        self.assertTrue(self.config_dir.exists())
        self.assertTrue(self.workspace.exists())

        # Cache should be populated
        self.assertEqual(config._CONFIG_CACHE, {})
        self.assertEqual(config._CONFIG_MTIME, 0.0)

    def test_save_and_load_config(self):
        test_conf = {"token": "12345", "user_id": 9876}
        config.save_config(test_conf)

        self.assertTrue(self.config_file.exists())
        self.assertEqual(config._CONFIG_CACHE, test_conf)
        self.assertNotEqual(config._CONFIG_MTIME, 0.0)

        # Loading should fetch from cache (we patch read_text to ensure it doesn't read again)
        with patch('myclaw.config.Path.read_text', side_effect=Exception("Should not be called!")):
            loaded_conf = config.load_config()
            self.assertEqual(loaded_conf, test_conf)

    def test_load_config_cache_invalidation(self):
        # Initial save
        test_conf = {"key": "val1"}
        config.save_config(test_conf)

        # Wait slightly to ensure mtime changes
        time.sleep(0.01)

        # External write to file bypassing save_config
        new_conf = {"key": "val2"}
        import json
        self.config_file.write_text(json.dumps(new_conf))

        # Now load_config should detect mtime change and reload
        loaded_conf = config.load_config()
        self.assertEqual(loaded_conf, new_conf)

    def test_config_mutation_protection(self):
        # Verify that modifying returned dictionary doesn't modify cache
        test_conf = {"key": "val1"}
        config.save_config(test_conf)

        loaded = config.load_config()
        loaded["key"] = "modified"

        # Cache should remain intact
        self.assertEqual(config._CONFIG_CACHE["key"], "val1")

if __name__ == '__main__':
    unittest.main()
