import unittest
from pathlib import Path
import tempfile
import shutil
import myclaw.tools as tools

class TestToolsSecurity(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to act as the WORKSPACE for testing
        self.test_dir = tempfile.mkdtemp()
        self.workspace_path = Path(self.test_dir)

        # Override the WORKSPACE variable in the tools module
        self.original_workspace = tools.WORKSPACE
        tools.WORKSPACE = self.workspace_path

        # Create a test file within the workspace
        self.test_file_path = self.workspace_path / "test.txt"
        self.test_file_path.write_text("Hello World")

        # Create a file outside the workspace to test traversal
        self.outside_dir = tempfile.mkdtemp()
        self.outside_file_path = Path(self.outside_dir) / "secret.txt"
        self.outside_file_path.write_text("Secret Data")

    def tearDown(self):
        # Restore the original WORKSPACE
        tools.WORKSPACE = self.original_workspace
        # Clean up temporary directories
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.outside_dir)

    def test_read_file_within_workspace(self):
        content = tools.read_file("test.txt")
        self.assertEqual(content, "Hello World")

    def test_read_file_path_traversal(self):
        # Attempt to read a file outside the workspace using path traversal
        traversal_path = f"../{Path(self.outside_dir).name}/secret.txt"
        content = tools.read_file(traversal_path)
        self.assertEqual(content, "Error: Access denied")

        # Attempt to read an absolute path outside the workspace
        absolute_path = str(self.outside_file_path)
        content = tools.read_file(absolute_path)
        self.assertEqual(content, "Error: Access denied")

    def test_write_file_within_workspace(self):
        result = tools.write_file("new_test.txt", "New Content")
        self.assertEqual(result, "File written: new_test.txt")
        content = (self.workspace_path / "new_test.txt").read_text()
        self.assertEqual(content, "New Content")

    def test_write_file_path_traversal(self):
        # Attempt to write a file outside the workspace using path traversal
        traversal_path = f"../{Path(self.outside_dir).name}/hacked.txt"
        result = tools.write_file(traversal_path, "Hacked Data")
        self.assertEqual(result, "Error: Access denied")

        # Ensure the file was not written
        self.assertFalse((Path(self.outside_dir) / "hacked.txt").exists())

    def test_read_file_exception_handling(self):
        # Attempt to read a non-existent file
        content = tools.read_file("nonexistent.txt")
        self.assertEqual(content, "Error: Access denied")

    def test_write_file_exception_handling(self):
        # Attempt to write to a directory that doesn't exist within the workspace
        result = tools.write_file("nonexistent_dir/new_file.txt", "Data")
        self.assertEqual(result, "Error: Access denied")

if __name__ == "__main__":
    unittest.main()
