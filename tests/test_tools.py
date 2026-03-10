import unittest
import tempfile
import shutil
from pathlib import Path
import os
import sys
from unittest.mock import patch

# Mock sys.modules for missing dependencies before importing
sys.modules['requests'] = unittest.mock.MagicMock()

import myclaw.tools as tools

class TestToolsSecurity(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for isolated workspace
        self.test_dir = tempfile.mkdtemp()
        self.workspace_path = Path(self.test_dir)

        # Override WORKSPACE in tools
        self.original_workspace = tools.WORKSPACE
        tools.WORKSPACE = self.workspace_path

        # Create a test file outside the workspace to simulate sensitive files
        self.outside_dir = tempfile.mkdtemp()
        self.secret_file = Path(self.outside_dir) / "secret.txt"
        self.secret_file.write_text("SUPER_SECRET")

    def tearDown(self):
        # Restore WORKSPACE
        tools.WORKSPACE = self.original_workspace

        # Clean up temporary directories
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.outside_dir)

    def test_write_read_file_valid(self):
        # Test valid file write and read inside workspace
        write_result = tools.write_file("test.txt", "Hello Workspace")
        self.assertEqual(write_result, "File written: test.txt")

        read_result = tools.read_file("test.txt")
        self.assertEqual(read_result, "Hello Workspace")

    def test_path_traversal_read(self):
        # Attempt to read a file outside the workspace using path traversal
        traversal_path = f"../{self.secret_file.name}"

        # Create a symlink/structure if we wanted, but standard traversal string is simpler
        rel_path = os.path.relpath(self.secret_file, self.workspace_path)

        result = tools.read_file(rel_path)
        self.assertEqual(result, "Error: Access denied")

        # Test absolute path read attempt
        result_absolute = tools.read_file(str(self.secret_file))
        self.assertEqual(result_absolute, "Error: Access denied")

    def test_path_traversal_write(self):
        # Attempt to write outside the workspace
        rel_path = os.path.relpath(self.secret_file, self.workspace_path)

        result = tools.write_file(rel_path, "MALICIOUS")
        self.assertEqual(result, "Error: Access denied")

        # Ensure the secret file was not modified
        self.assertEqual(self.secret_file.read_text(), "SUPER_SECRET")

        # Test absolute path write attempt
        abs_write_path = Path(self.outside_dir) / "new_malicious.txt"
        result_absolute = tools.write_file(str(abs_write_path), "MALICIOUS")
        self.assertEqual(result_absolute, "Error: Access denied")
        self.assertFalse(abs_write_path.exists())

    def test_exception_leakage_read(self):
        # Attempt to read a non-existent file
        result = tools.read_file("nonexistent.txt")
        # Ensure it returns generic error, not FileNotFoundError string
        self.assertEqual(result, "Error: Access denied")

if __name__ == '__main__':
    unittest.main()