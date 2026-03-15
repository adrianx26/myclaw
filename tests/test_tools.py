import unittest
import tempfile
import shutil
from pathlib import Path
import myclaw.tools

class TestTools(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_workspace = myclaw.tools.WORKSPACE
        myclaw.tools.WORKSPACE = Path(self.temp_dir)

    def tearDown(self):
        myclaw.tools.WORKSPACE = self.original_workspace
        shutil.rmtree(self.temp_dir)

    def test_read_write_valid_file(self):
        result = myclaw.tools.write_file("test.txt", "hello")
        self.assertEqual(result, "File written: test.txt")
        result = myclaw.tools.read_file("test.txt")
        self.assertEqual(result, "hello")

    def test_path_traversal_absolute(self):
        result = myclaw.tools.read_file("/etc/passwd")
        # should fail safely
        self.assertEqual(result, "Error: Access denied")

    def test_path_traversal_relative(self):
        result = myclaw.tools.read_file("../../../../../etc/passwd")
        # should fail safely
        self.assertEqual(result, "Error: Access denied")

    def test_read_file_not_found(self):
        result = myclaw.tools.read_file("nonexistent_file.txt")
        self.assertEqual(result, "Error: File not found")

if __name__ == "__main__":
    unittest.main()
