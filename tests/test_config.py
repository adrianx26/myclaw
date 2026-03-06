import unittest
import json
from pathlib import Path
import tempfile
import myclaw.config as config_module

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / ".myclaw"
        self.config_file = self.config_dir / "config.json"
        self.workspace = self.config_dir / "workspace"

        self._orig_dir = config_module.CONFIG_DIR
        self._orig_file = config_module.CONFIG_FILE
        self._orig_workspace = config_module.WORKSPACE
        self._orig_cache = getattr(config_module, '_CONFIG_CACHE', None)

        config_module.CONFIG_DIR = self.config_dir
        config_module.CONFIG_FILE = self.config_file
        config_module.WORKSPACE = self.workspace
        if hasattr(config_module, '_CONFIG_CACHE'):
            config_module._CONFIG_CACHE = None

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
        config_module.CONFIG_DIR = self._orig_dir
        config_module.CONFIG_FILE = self._orig_file
        config_module.WORKSPACE = self._orig_workspace
        if hasattr(config_module, '_CONFIG_CACHE'):
            config_module._CONFIG_CACHE = self._orig_cache

    def test_load_empty(self):
        data = config_module.load_config()
        self.assertEqual(data, {})

    def test_save_and_load(self):
        test_data = {"key": "value"}
        config_module.save_config(test_data)
        loaded = config_module.load_config()
        self.assertEqual(loaded, test_data)

    def test_cache_mutability(self):
        test_data = {"key": "value", "nested": {"list": [1, 2, 3]}}
        config_module.save_config(test_data)

        # Load and mutate
        loaded1 = config_module.load_config()
        loaded1["key"] = "changed"
        loaded1["nested"]["list"].append(4)

        # Load again, should be original (including deep objects)
        loaded2 = config_module.load_config()
        self.assertEqual(loaded2["key"], "value")
        self.assertEqual(loaded2["nested"]["list"], [1, 2, 3])

if __name__ == '__main__':
    unittest.main()
