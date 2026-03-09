import unittest
import tempfile
import shutil
from pathlib import Path
import os
import myclaw.tools as tools

class TestTools(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to act as the workspace
        self.test_dir = tempfile.mkdtemp()
        self.workspace_path = Path(self.test_dir)

        # Override the module's WORKSPACE variable for testing
        self.original_workspace = tools.WORKSPACE
        tools.WORKSPACE = self.workspace_path

    def tearDown(self):
        # Restore the original WORKSPACE and clean up the temp directory
        tools.WORKSPACE = self.original_workspace
        shutil.rmtree(self.test_dir)

    def test_write_file_success(self):
        result = tools.write_file("test.txt", "hello")
        self.assertEqual(result, "File written: test.txt")
        self.assertTrue((self.workspace_path / "test.txt").exists())
        self.assertEqual((self.workspace_path / "test.txt").read_text(), "hello")

    def test_read_file_success(self):
        (self.workspace_path / "read_test.txt").write_text("world")
        result = tools.read_file("read_test.txt")
        self.assertEqual(result, "world")

    def test_write_file_path_traversal(self):
        # Attempt to write outside the workspace
        result = tools.write_file("../test_traversal.txt", "hacked")
        self.assertEqual(result, "Error: Access denied")
        self.assertFalse((self.workspace_path.parent / "test_traversal.txt").exists())

    def test_read_file_path_traversal(self):
        # Attempt to read outside the workspace
        outside_file = self.workspace_path.parent / "test_read_traversal.txt"
        outside_file.write_text("secret")
        try:
            result = tools.read_file("../test_read_traversal.txt")
            self.assertEqual(result, "Error: Access denied")
        finally:
            if outside_file.exists():
                os.remove(outside_file)

    def test_write_file_absolute_path(self):
        # Attempt to write using an absolute path (which Python pathlib '/' operator resolves to the absolute path)
        result = tools.write_file("/tmp/hacked_file.txt", "hacked")
        self.assertEqual(result, "Error: Access denied")
        self.assertFalse(Path("/tmp/hacked_file.txt").exists())

    def test_read_file_absolute_path(self):
        # Attempt to read an absolute path
        result = tools.read_file("/etc/passwd")
        self.assertEqual(result, "Error: Access denied")

    def test_read_file_missing_exception_leakage(self):
        # Attempt to read a missing file; should not leak exception message
        result = tools.read_file("nonexistent.txt")
        self.assertEqual(result, "Error: Access denied")

if __name__ == '__main__':
    unittest.main()
