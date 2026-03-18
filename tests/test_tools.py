import unittest
import tempfile
import shutil
from pathlib import Path

# Need to patch WORKSPACE before importing the module functions that use it
import myclaw.tools as tools

class TestTools(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to act as WORKSPACE
        self.test_dir = tempfile.mkdtemp()
        self.workspace = Path(self.test_dir)

        # Patch the global WORKSPACE in myclaw.tools
        self.original_workspace = tools.WORKSPACE
        tools.WORKSPACE = self.workspace

        # Create a test file
        (self.workspace / "test.txt").write_text("hello world")

    def tearDown(self):
        # Restore the original WORKSPACE
        tools.WORKSPACE = self.original_workspace

        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_read_file_normal(self):
        result = tools.read_file("test.txt")
        self.assertEqual(result, "hello world")

    def test_read_file_not_found(self):
        result = tools.read_file("nonexistent.txt")
        self.assertEqual(result, "Error: File not found")

    def test_read_file_absolute_path(self):
        # Attempt to read an absolute path (should be restricted to workspace)
        # Even if /etc/passwd exists, the target will be treated as workspace/etc/passwd
        result = tools.read_file("/etc/passwd")
        self.assertEqual(result, "Error: File not found")

    def test_read_file_path_traversal(self):
        # Attempt to traverse outside the workspace
        result = tools.read_file("../../../etc/passwd")
        self.assertEqual(result, "Error: Access denied")

    def test_write_file_normal(self):
        result = tools.write_file("new_file.txt", "test content")
        self.assertEqual(result, "File written: new_file.txt")
        content = (self.workspace / "new_file.txt").read_text()
        self.assertEqual(content, "test content")

    def test_write_file_path_traversal(self):
        # Attempt to write outside the workspace
        result = tools.write_file("../../../tmp/hacked.txt", "hacked")
        self.assertEqual(result, "Error: Access denied")

if __name__ == '__main__':
    unittest.main()