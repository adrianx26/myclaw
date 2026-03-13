import unittest
import tempfile
import shutil
from pathlib import Path

import myclaw.tools as tools

class TestToolsSecurity(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to act as the WORKSPACE for testing
        self.test_dir = tempfile.mkdtemp()
        self.workspace_path = Path(self.test_dir)

        # Override the global WORKSPACE in the tools module
        self.original_workspace = tools.WORKSPACE
        tools.WORKSPACE = self.workspace_path

        # Create a test file in the workspace
        self.test_file_path = self.workspace_path / "test.txt"
        self.test_file_path.write_text("hello world")

    def tearDown(self):
        # Restore the original WORKSPACE and clean up the temporary directory
        tools.WORKSPACE = self.original_workspace
        shutil.rmtree(self.test_dir)

    def test_read_file_success(self):
        result = tools.read_file("test.txt")
        self.assertEqual(result, "hello world")

    def test_write_file_success(self):
        result = tools.write_file("new_test.txt", "new content")
        self.assertEqual(result, "File written: new_test.txt")
        self.assertEqual((self.workspace_path / "new_test.txt").read_text(), "new content")

    def test_read_file_path_traversal(self):
        # Attempt to read a file outside the workspace using path traversal
        result = tools.read_file("../../../../../../etc/passwd")
        self.assertEqual(result, "Error: Access denied")

    def test_write_file_path_traversal(self):
        # Attempt to write a file outside the workspace using path traversal
        result = tools.write_file("../../../../../../tmp/test_hack.txt", "hacked")
        self.assertEqual(result, "Error: Access denied")
        self.assertFalse(Path("/tmp/test_hack.txt").exists())

    def test_read_file_absolute_path(self):
        # Attempt to read an absolute path outside the workspace
        result = tools.read_file("/etc/passwd")
        self.assertEqual(result, "Error: Access denied")

    def test_write_file_absolute_path(self):
        # Attempt to write to an absolute path outside the workspace
        result = tools.write_file("/tmp/test_hack2.txt", "hacked")
        self.assertEqual(result, "Error: Access denied")
        self.assertFalse(Path("/tmp/test_hack2.txt").exists())

    def test_read_file_generic_error(self):
        # Attempt to read a file that doesn't exist to test generic error message
        result = tools.read_file("non_existent_file.txt")
        self.assertEqual(result, "Error: Access denied")

if __name__ == '__main__':
    unittest.main()
