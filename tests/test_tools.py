import unittest
import tempfile
import shutil
from pathlib import Path
import myclaw.tools as tools

class TestTools(unittest.TestCase):
    def setUp(self):
        # Isolate the test environment with a temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir).resolve()

        # Override WORKSPACE in tools
        self.original_workspace = tools.WORKSPACE
        tools.WORKSPACE = self.temp_path

        # Create a test file
        self.test_file_path = self.temp_path / "test.txt"
        self.test_file_path.write_text("hello world")

    def tearDown(self):
        # Restore original WORKSPACE
        tools.WORKSPACE = self.original_workspace
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)

    def test_read_file_success(self):
        result = tools.read_file("test.txt")
        self.assertEqual(result, "hello world")

    def test_read_file_not_found(self):
        result = tools.read_file("nonexistent.txt")
        self.assertEqual(result, "Error: File not found")

    def test_read_file_path_traversal(self):
        # Attempt to read a file outside the workspace using ../
        result = tools.read_file("../test.txt")
        self.assertEqual(result, "Error: Access denied")

        # Attempt to read a file outside the workspace using absolute path
        result = tools.read_file("/etc/passwd")
        self.assertEqual(result, "Error: Access denied")

    def test_write_file_success(self):
        result = tools.write_file("new_test.txt", "new content")
        self.assertEqual(result, "File written: new_test.txt")

        # Verify it was actually written
        content = (self.temp_path / "new_test.txt").read_text()
        self.assertEqual(content, "new content")

    def test_write_file_path_traversal(self):
        # Attempt to write outside workspace using ../
        result = tools.write_file("../new_test.txt", "evil")
        self.assertEqual(result, "Error: Access denied")

        # Attempt to write outside workspace using absolute path
        result = tools.write_file("/tmp/evil.txt", "evil")
        self.assertEqual(result, "Error: Access denied")

if __name__ == "__main__":
    unittest.main()
