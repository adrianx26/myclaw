import unittest
import tempfile
import shutil
import os
from pathlib import Path
import myclaw.tools

class TestTools(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for the workspace
        self.test_workspace = tempfile.mkdtemp()
        self.original_workspace = myclaw.tools.WORKSPACE
        myclaw.tools.WORKSPACE = Path(self.test_workspace)

        # Create a test file inside the workspace
        self.test_file_path = Path(self.test_workspace) / "test.txt"
        self.test_file_path.write_text("hello world")

        # Create a test file outside the workspace
        self.outside_dir = tempfile.mkdtemp()
        self.outside_file_path = Path(self.outside_dir) / "secret.txt"
        self.outside_file_path.write_text("secret data")

    def tearDown(self):
        # Restore the original workspace
        myclaw.tools.WORKSPACE = self.original_workspace

        # Clean up temporary directories
        shutil.rmtree(self.test_workspace)
        shutil.rmtree(self.outside_dir)

    def test_read_file_success(self):
        """Test reading a file within the workspace"""
        content = myclaw.tools.read_file("test.txt")
        self.assertEqual(content, "hello world")

    def test_read_file_path_traversal(self):
        """Test that path traversal outside the workspace is denied"""
        # Attempt to read the file outside the workspace
        relative_path = os.path.relpath(self.outside_file_path, self.test_workspace)
        content = myclaw.tools.read_file(relative_path)
        self.assertEqual(content, "Error: Access denied")

        # Another test for absolute path
        content_absolute = myclaw.tools.read_file(str(self.outside_file_path))
        self.assertEqual(content_absolute, "Error: Access denied")

    def test_write_file_success(self):
        """Test writing a file within the workspace"""
        result = myclaw.tools.write_file("new_test.txt", "new content")
        self.assertEqual(result, "File written: new_test.txt")

        # Verify it was written
        new_file_path = Path(self.test_workspace) / "new_test.txt"
        self.assertTrue(new_file_path.exists())
        self.assertEqual(new_file_path.read_text(), "new content")

    def test_write_file_path_traversal(self):
        """Test that path traversal outside the workspace for writing is denied"""
        relative_path = os.path.relpath(self.outside_file_path, self.test_workspace)
        result = myclaw.tools.write_file(relative_path, "hacked")
        self.assertEqual(result, "Error: Access denied")

        # Verify the file was not modified
        self.assertEqual(self.outside_file_path.read_text(), "secret data")

if __name__ == '__main__':
    unittest.main()
