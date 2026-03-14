import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
import shutil

import myclaw.tools


class TestToolsSecurity(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to act as the workspace for tests
        self.test_dir = tempfile.mkdtemp()
        self.workspace_path = Path(self.test_dir)

        # Override WORKSPACE in tools to isolate tests
        self.patcher = patch('myclaw.tools.WORKSPACE', self.workspace_path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.test_dir)

    def test_read_file_path_traversal(self):
        # Attempt path traversal outside the workspace
        result = myclaw.tools.read_file("../../../../../../etc/passwd")
        self.assertEqual(result, "Error: Access denied")

    def test_write_file_path_traversal(self):
        # Attempt path traversal outside the workspace
        result = myclaw.tools.write_file("../../../../../../etc/passwd", "malicious_content")
        self.assertEqual(result, "Error: Access denied")

    def test_read_file_exception_handling(self):
        # Trigger FileNotFoundError which should be caught and replaced with specific error message
        result = myclaw.tools.read_file("non_existent_file.txt")
        self.assertEqual(result, "Error: File not found")

    def test_write_file_exception_handling(self):
        # Trigger PermissionError (or similar) by trying to write to a directory
        (self.workspace_path / "a_directory").mkdir()
        result = myclaw.tools.write_file("a_directory", "content")
        self.assertEqual(result, "Error: Access denied")

    def test_read_file_legitimate(self):
        # Ensure normal reading works
        test_file = self.workspace_path / "test.txt"
        test_file.write_text("hello world")

        result = myclaw.tools.read_file("test.txt")
        self.assertEqual(result, "hello world")

    def test_write_file_legitimate(self):
        # Ensure normal writing works
        result = myclaw.tools.write_file("test_write.txt", "hello world")
        self.assertEqual(result, "File written: test_write.txt")

        # Verify it was actually written
        content = (self.workspace_path / "test_write.txt").read_text()
        self.assertEqual(content, "hello world")

if __name__ == '__main__':
    unittest.main()
