import unittest
from pathlib import Path
import tempfile
import shutil

import myclaw.tools as tools

class TestToolsSecurity(unittest.TestCase):
    def setUp(self):
        # Isolate the test environment using a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.workspace = Path(self.test_dir) / "workspace"
        self.workspace.mkdir()

        # Override the WORKSPACE variable in the module
        self._old_workspace = tools.WORKSPACE
        tools.WORKSPACE = self.workspace

        # Create a test file
        self.test_file = self.workspace / "test.txt"
        self.test_file.write_text("hello world")

        # Create a file outside the workspace to simulate sensitive data
        self.sensitive_file = Path(self.test_dir) / "passwd"
        self.sensitive_file.write_text("secret:data")

    def tearDown(self):
        # Restore the original WORKSPACE variable
        tools.WORKSPACE = self._old_workspace
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_read_file_success(self):
        # Should be able to read a file inside the workspace
        result = tools.read_file("test.txt")
        self.assertEqual(result, "hello world")

    def test_read_file_traversal(self):
        # Should block path traversal attempts
        result = tools.read_file("../passwd")
        self.assertEqual(result, "Error: Access denied")

        # Absolute path outside workspace should also be blocked
        result = tools.read_file(str(self.sensitive_file.resolve()))
        self.assertEqual(result, "Error: Access denied")

    def test_write_file_success(self):
        # Should be able to write a file inside the workspace
        result = tools.write_file("new_file.txt", "new content")
        self.assertEqual(result, "File written: new_file.txt")
        self.assertTrue((self.workspace / "new_file.txt").exists())
        self.assertEqual((self.workspace / "new_file.txt").read_text(), "new content")

    def test_write_file_traversal(self):
        # Should block path traversal attempts
        result = tools.write_file("../hacked.txt", "hacked")
        self.assertEqual(result, "Error: Access denied")
        self.assertFalse((Path(self.test_dir) / "hacked.txt").exists())

    def test_read_file_fails_securely(self):
        # Non-existent file should fail securely
        result = tools.read_file("nonexistent.txt")
        self.assertEqual(result, "Error reading file")

if __name__ == '__main__':
    unittest.main()
