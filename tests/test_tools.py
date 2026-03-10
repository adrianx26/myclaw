import unittest
import tempfile
import shutil
from pathlib import Path
import myclaw.tools

class TestToolsSecurity(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.workspace_path = Path(self.test_dir) / "workspace"
        self.workspace_path.mkdir()

        # Override WORKSPACE for tests
        self.original_workspace = myclaw.tools.WORKSPACE
        myclaw.tools.WORKSPACE = self.workspace_path

        # Create a test file inside workspace
        self.safe_file = self.workspace_path / "safe.txt"
        self.safe_file.write_text("safe content")

        # Create a test file outside workspace
        self.secret_file = Path(self.test_dir) / "secret.txt"
        self.secret_file.write_text("secret content")

    def tearDown(self):
        # Restore WORKSPACE and cleanup
        myclaw.tools.WORKSPACE = self.original_workspace
        shutil.rmtree(self.test_dir)

    def test_read_file_safe(self):
        result = myclaw.tools.read_file("safe.txt")
        self.assertEqual(result, "safe content")

    def test_read_file_path_traversal_relative(self):
        # Should not be able to read ../secret.txt
        result = myclaw.tools.read_file("../secret.txt")
        self.assertEqual(result, "Error: Access denied")

    def test_read_file_path_traversal_absolute(self):
        # Should not be able to read absolute path
        result = myclaw.tools.read_file(str(self.secret_file))
        self.assertEqual(result, "Error: Access denied")

    def test_write_file_safe(self):
        result = myclaw.tools.write_file("new_safe.txt", "new content")
        self.assertEqual(result, "File written: new_safe.txt")
        self.assertEqual((self.workspace_path / "new_safe.txt").read_text(), "new content")

    def test_write_file_path_traversal_relative(self):
        # Should not be able to write ../hacked.txt
        result = myclaw.tools.write_file("../hacked.txt", "hacked")
        self.assertEqual(result, "Error: Access denied")
        self.assertFalse((Path(self.test_dir) / "hacked.txt").exists())

    def test_write_file_path_traversal_absolute(self):
        # Should not be able to write absolute path
        hacked_file = Path(self.test_dir) / "hacked_abs.txt"
        result = myclaw.tools.write_file(str(hacked_file), "hacked")
        self.assertEqual(result, "Error: Access denied")
        self.assertFalse(hacked_file.exists())

if __name__ == "__main__":
    unittest.main()
