import unittest
from pathlib import Path
import os
import shutil
import tempfile

from myclaw.tools import read_file, write_file, WORKSPACE

class TestToolsSecurity(unittest.TestCase):
    def setUp(self):
        # Create a temporary workspace directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.workspace_dir = Path(self.test_dir) / "workspace"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        # Override WORKSPACE temporarily for the tests
        self.original_workspace = WORKSPACE
        import myclaw.tools
        myclaw.tools.WORKSPACE = self.workspace_dir

        # Setup a file inside workspace
        self.valid_file = self.workspace_dir / "test.txt"
        self.valid_file.write_text("hello world")

        # Setup a file outside workspace
        self.outside_file = Path(self.test_dir) / "secret.txt"
        self.outside_file.write_text("super secret")

    def tearDown(self):
        # Restore WORKSPACE
        import myclaw.tools
        myclaw.tools.WORKSPACE = self.original_workspace

        # Cleanup
        shutil.rmtree(self.test_dir)

    def test_read_file_valid(self):
        result = read_file("test.txt")
        self.assertEqual(result, "hello world")

    def test_read_file_path_traversal(self):
        result = read_file("../secret.txt")
        self.assertEqual(result, "Error: Access denied. File operations are restricted to the workspace.")

    def test_read_file_absolute_path_traversal(self):
        result = read_file(str(self.outside_file.resolve()))
        self.assertEqual(result, "Error: Access denied. File operations are restricted to the workspace.")

    def test_write_file_valid(self):
        result = write_file("new_test.txt", "new content")
        self.assertEqual(result, "File written: new_test.txt")
        self.assertEqual((self.workspace_dir / "new_test.txt").read_text(), "new content")

    def test_write_file_path_traversal(self):
        result = write_file("../hacked.txt", "hacked content")
        self.assertEqual(result, "Error: Access denied. File operations are restricted to the workspace.")
        self.assertFalse((Path(self.test_dir) / "hacked.txt").exists())

    def test_write_file_absolute_path_traversal(self):
        target = Path(self.test_dir) / "hacked_absolute.txt"
        result = write_file(str(target.resolve()), "hacked content")
        self.assertEqual(result, "Error: Access denied. File operations are restricted to the workspace.")
        self.assertFalse(target.exists())
