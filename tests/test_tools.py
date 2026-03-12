import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
import myclaw.tools as tools

class TestTools(unittest.TestCase):
    def setUp(self):
        # Isolate the test environment using a temporary workspace directory
        self.test_workspace = Path(tempfile.mkdtemp())
        self.original_workspace = tools.WORKSPACE
        tools.WORKSPACE = self.test_workspace

    def tearDown(self):
        # Restore the original workspace and clean up the temporary directory
        tools.WORKSPACE = self.original_workspace
        shutil.rmtree(self.test_workspace)

    def test_read_file_path_traversal(self):
        # Try to read outside the workspace
        result = tools.read_file("../../../../../../../../etc/passwd")
        self.assertEqual(result, "Error: Access denied")

        result = tools.read_file("/etc/passwd")
        self.assertEqual(result, "Error: Access denied")

    def test_write_file_path_traversal(self):
        # Try to write outside the workspace
        result = tools.write_file("../../../../../../../../tmp/hacked.txt", "hacked")
        self.assertEqual(result, "Error: Access denied")

        result = tools.write_file("/tmp/hacked2.txt", "hacked")
        self.assertEqual(result, "Error: Access denied")

    def test_read_write_file_success(self):
        # Valid write and read inside the workspace
        write_result = tools.write_file("test.txt", "hello world")
        self.assertEqual(write_result, "File written: test.txt")

        read_result = tools.read_file("test.txt")
        self.assertEqual(read_result, "hello world")

    def test_read_file_not_found(self):
        # Reading a non-existent file inside the workspace should securely fail
        result = tools.read_file("nonexistent.txt")
        self.assertEqual(result, "Error: Access denied")

    @patch("subprocess.run")
    def test_shell_exception(self, mock_run):
        # Simulate a subprocess exception
        mock_run.side_effect = Exception("Hidden error details")
        result = tools.shell("ls")
        # Ensure the underlying exception message is not leaked
        self.assertEqual(result, "Error: Command failed")

if __name__ == "__main__":
    unittest.main()
