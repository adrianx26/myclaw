import unittest
import tempfile
import shutil
from pathlib import Path

# Need to patch myclaw.tools.WORKSPACE for the tests
import myclaw.tools as tools

class TestToolsSecurity(unittest.TestCase):
    def setUp(self):
        # Create a temporary workspace directory for tests
        self.test_dir = tempfile.mkdtemp()
        self.original_workspace = tools.WORKSPACE
        tools.WORKSPACE = Path(self.test_dir)

        # Create a dummy file in the workspace
        self.safe_file = tools.WORKSPACE / "safe.txt"
        self.safe_file.write_text("safe content")

    def tearDown(self):
        # Restore the original workspace and clean up temp dir
        tools.WORKSPACE = self.original_workspace
        shutil.rmtree(self.test_dir)

    def test_read_file_safe(self):
        result = tools.read_file("safe.txt")
        self.assertEqual(result, "safe content")

    def test_read_file_path_traversal(self):
        # Try to read outside the workspace
        # Assuming the temp dir is /tmp/something, we'll try to read /etc/passwd
        # or just traverse up
        result = tools.read_file("../../../../../../../../../../../../../../../etc/passwd")
        self.assertEqual(result, "Error: Access denied")

        # Try absolute path outside workspace
        result = tools.read_file("/etc/passwd")
        self.assertEqual(result, "Error: Access denied")

    def test_read_file_not_found(self):
        result = tools.read_file("nonexistent.txt")
        self.assertEqual(result, "Error: File not found")

    def test_write_file_safe(self):
        result = tools.write_file("new_safe.txt", "new content")
        self.assertEqual(result, "File written: new_safe.txt")
        self.assertEqual((tools.WORKSPACE / "new_safe.txt").read_text(), "new content")

    def test_write_file_path_traversal(self):
        # Try to write outside the workspace
        result = tools.write_file("../../../../../../../../../../../../../../../tmp/hacked.txt", "hacked")
        self.assertEqual(result, "Error: Access denied")

        # Try absolute path outside workspace
        result = tools.write_file("/tmp/hacked_absolute.txt", "hacked")
        self.assertEqual(result, "Error: Access denied")

if __name__ == '__main__':
    unittest.main()
