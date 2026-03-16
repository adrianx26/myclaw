import unittest
import tempfile
import shutil
from pathlib import Path
import os
import myclaw.tools

class TestToolsSecurity(unittest.TestCase):
    def setUp(self):
        # Isolate tests with temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.original_workspace = myclaw.tools.WORKSPACE
        # Set WORKSPACE to resolved temp directory for accurate testing
        myclaw.tools.WORKSPACE = Path(self.temp_dir).resolve()

        # Create a sample file inside workspace
        self.safe_file = myclaw.tools.WORKSPACE / "safe.txt"
        self.safe_file.write_text("safe content")

        # Create a file outside workspace to simulate target
        self.outside_dir = tempfile.mkdtemp()
        self.secret_file = Path(self.outside_dir).resolve() / "secret.txt"
        self.secret_file.write_text("secret content")

    def tearDown(self):
        # Restore WORKSPACE and cleanup
        myclaw.tools.WORKSPACE = self.original_workspace
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.outside_dir)

    def test_read_file_safe(self):
        # Should read files inside workspace
        content = myclaw.tools.read_file("safe.txt")
        self.assertEqual(content, "safe content")

    def test_read_file_not_found(self):
        # Should return specific error for missing files instead of generic exception
        content = myclaw.tools.read_file("missing.txt")
        self.assertEqual(content, "Error: File not found")

    def test_read_file_path_traversal_relative(self):
        # Should deny reading files outside using ../
        # Calculate relative path from temp_dir to secret_file
        rel_path = os.path.relpath(self.secret_file, self.temp_dir)
        content = myclaw.tools.read_file(rel_path)
        self.assertEqual(content, "Error: Access denied")

    def test_read_file_path_traversal_absolute(self):
        # Should deny reading files using absolute paths
        content = myclaw.tools.read_file(str(self.secret_file))
        self.assertEqual(content, "Error: Access denied")

    def test_write_file_safe(self):
        # Should write files inside workspace
        result = myclaw.tools.write_file("new_file.txt", "new content")
        self.assertEqual(result, "File written: new_file.txt")
        content = (myclaw.tools.WORKSPACE / "new_file.txt").read_text()
        self.assertEqual(content, "new content")

    def test_write_file_path_traversal_relative(self):
        # Should deny writing files outside using ../
        # Calculate relative path from temp_dir to outside_dir/hack.txt
        target = Path(self.outside_dir).resolve() / "hack.txt"
        rel_path = os.path.relpath(target, self.temp_dir)
        result = myclaw.tools.write_file(rel_path, "hacked")
        self.assertEqual(result, "Error: Access denied")
        self.assertFalse(target.exists())

    def test_write_file_path_traversal_absolute(self):
        # Should deny writing files using absolute paths
        target = Path(self.outside_dir).resolve() / "hack.txt"
        result = myclaw.tools.write_file(str(target), "hacked")
        self.assertEqual(result, "Error: Access denied")
        self.assertFalse(target.exists())
