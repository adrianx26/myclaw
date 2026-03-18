import unittest
import tempfile
import shutil
from pathlib import Path

# Important: Patch WORKSPACE for testing
import myclaw.tools as tools

class TestToolsSecurity(unittest.TestCase):
    def setUp(self):
        # Create a temporary workspace
        self.test_dir = tempfile.mkdtemp()
        self.workspace_path = Path(self.test_dir) / "workspace"
        self.workspace_path.mkdir()

        # Override the WORKSPACE variable in tools module
        self.original_workspace = tools.WORKSPACE
        tools.WORKSPACE = self.workspace_path

    def tearDown(self):
        # Restore the original WORKSPACE and clean up
        tools.WORKSPACE = self.original_workspace
        shutil.rmtree(self.test_dir)

    def test_read_file_valid(self):
        # Create a valid file within workspace
        test_file = self.workspace_path / "valid.txt"
        test_file.write_text("Hello, world!")

        result = tools.read_file("valid.txt")
        self.assertEqual(result, "Hello, world!")

    def test_read_file_path_traversal_relative(self):
        # Create a file outside workspace
        outside_file = Path(self.test_dir) / "secret.txt"
        outside_file.write_text("Secret Data")

        # Attempt path traversal
        result = tools.read_file("../secret.txt")
        self.assertEqual(result, "Error: Access denied")

    def test_read_file_path_traversal_absolute(self):
        # Try to read an absolute system file
        # Using pathlib's behavior with '/' and absolute path strings
        result = tools.read_file("/etc/passwd")
        self.assertEqual(result, "Error: Access denied")

    def test_read_file_not_found(self):
        result = tools.read_file("nonexistent.txt")
        self.assertEqual(result, "Error: File not found")

    def test_write_file_valid(self):
        result = tools.write_file("new_file.txt", "New content")
        self.assertEqual(result, "File written: new_file.txt")

        # Verify the file was written
        content = (self.workspace_path / "new_file.txt").read_text()
        self.assertEqual(content, "New content")

    def test_write_file_path_traversal_relative(self):
        # Attempt to write outside workspace
        result = tools.write_file("../hacked.txt", "Malicious content")
        self.assertEqual(result, "Error: Access denied")

        # Verify the file was NOT written
        self.assertFalse((Path(self.test_dir) / "hacked.txt").exists())

    def test_write_file_path_traversal_absolute(self):
        # Try to write to an absolute path
        # Note: writing to /etc might fail due to permissions, but we expect our code
        # to catch it as Access denied due to boundaries before trying the write operation
        result = tools.write_file("/tmp/hacked.txt", "Malicious content")
        self.assertEqual(result, "Error: Access denied")

if __name__ == '__main__':
    unittest.main()
