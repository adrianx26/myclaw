import unittest
import tempfile
from pathlib import Path
import shutil
import myclaw.tools
from myclaw.tools import read_file, write_file, shell

class TestTools(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir) / "workspace"
        self.workspace.mkdir()
        # Override WORKSPACE
        self.old_workspace = myclaw.tools.WORKSPACE
        myclaw.tools.WORKSPACE = self.workspace

    def tearDown(self):
        # Restore WORKSPACE
        myclaw.tools.WORKSPACE = self.old_workspace
        shutil.rmtree(self.temp_dir)

    def test_write_and_read_file_normal(self):
        write_file("test.txt", "hello world")
        content = read_file("test.txt")
        self.assertEqual(content, "hello world")
        self.assertTrue((self.workspace / "test.txt").exists())

    def test_write_file_path_traversal_absolute(self):
        result = write_file("/tmp/test.txt", "hello world")
        self.assertEqual(result, "Error: Access denied")
        self.assertFalse(Path("/tmp/test.txt").exists() and (self.workspace / "/tmp/test.txt").exists())

    def test_write_file_path_traversal_relative(self):
        result = write_file("../test.txt", "hello world")
        self.assertEqual(result, "Error: Access denied")
        self.assertFalse((Path(self.temp_dir) / "test.txt").exists())

    def test_read_file_path_traversal_absolute(self):
        result = read_file("/etc/passwd")
        self.assertEqual(result, "Error: Access denied")

    def test_read_file_path_traversal_relative(self):
        result = read_file("../test.txt")
        self.assertEqual(result, "Error: Access denied")

    def test_read_file_not_found(self):
        result = read_file("does_not_exist.txt")
        self.assertEqual(result, "Error: Access denied")

if __name__ == '__main__':
    unittest.main()
