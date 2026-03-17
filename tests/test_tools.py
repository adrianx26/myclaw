import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import shutil
import myclaw.tools as tools

class TestTools(unittest.TestCase):
    def setUp(self):
        self.temp_workspace = Path(tempfile.mkdtemp())
        self.original_workspace = tools.WORKSPACE
        tools.WORKSPACE = self.temp_workspace

    def tearDown(self):
        tools.WORKSPACE = self.original_workspace
        shutil.rmtree(self.temp_workspace)

    def test_read_file_success(self):
        test_file = self.temp_workspace / "test.txt"
        test_file.write_text("hello")
        self.assertEqual(tools.read_file("test.txt"), "hello")

    def test_read_file_not_found(self):
        self.assertEqual(tools.read_file("not_exist.txt"), "Error: File not found")

    def test_read_file_path_traversal(self):
        self.assertEqual(tools.read_file("../../../../etc/passwd"), "Error: Access denied")
        self.assertEqual(tools.read_file("/etc/passwd"), "Error: Access denied")

    def test_write_file_success(self):
        result = tools.write_file("test2.txt", "world")
        self.assertEqual(result, "File written: test2.txt")
        self.assertEqual((self.temp_workspace / "test2.txt").read_text(), "world")

    def test_write_file_path_traversal(self):
        self.assertEqual(tools.write_file("../../../../etc/passwd", "world"), "Error: Access denied")
        self.assertEqual(tools.write_file("/etc/passwd", "world"), "Error: Access denied")

    def test_read_file_generic_exception(self):
        with patch("pathlib.Path.read_text", side_effect=PermissionError("Permission denied")):
            test_file = self.temp_workspace / "test3.txt"
            test_file.touch()
            self.assertEqual(tools.read_file("test3.txt"), "Error: Access denied")

    def test_write_file_generic_exception(self):
        with patch("pathlib.Path.write_text", side_effect=PermissionError("Permission denied")):
            self.assertEqual(tools.write_file("test4.txt", "world"), "Error: Access denied")

if __name__ == '__main__':
    unittest.main()