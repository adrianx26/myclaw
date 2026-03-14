import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

import myclaw.tools as tools

class TestToolsSecurity(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.workspace_path = Path(self.temp_dir)
        # Patch the tools WORKSPACE
        self.patcher = patch('myclaw.tools.WORKSPACE', self.workspace_path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.temp_dir)

    def test_read_file_path_traversal(self):
        # Setup a file outside the workspace
        outside_file = self.workspace_path.parent / "secret.txt"
        outside_file.write_text("secret_data")

        try:
            # Attempt to read outside the workspace
            relative_path = f"../{outside_file.name}"
            result = tools.read_file(relative_path)

            # The result should be a generic error
            self.assertEqual(result, "Error: Access denied")
        finally:
            if outside_file.exists():
                outside_file.unlink()

    def test_read_file_absolute_path(self):
        # Create a file outside workspace
        outside_file = self.workspace_path.parent / "secret2.txt"
        outside_file.write_text("secret_data2")

        try:
            # Attempt to read absolute path
            result = tools.read_file(str(outside_file.resolve()))

            # The result should be a generic error
            self.assertEqual(result, "Error: Access denied")
        finally:
            if outside_file.exists():
                outside_file.unlink()

    def test_write_file_path_traversal(self):
        # Attempt to write outside the workspace
        outside_file = self.workspace_path.parent / "hacked.txt"

        try:
            relative_path = f"../{outside_file.name}"
            result = tools.write_file(relative_path, "hacked_data")

            self.assertEqual(result, "Error: Access denied")
            self.assertFalse(outside_file.exists())
        finally:
            if outside_file.exists():
                outside_file.unlink()

    def test_write_file_absolute_path(self):
        outside_file = self.workspace_path.parent / "hacked2.txt"

        try:
            result = tools.write_file(str(outside_file.resolve()), "hacked_data")

            self.assertEqual(result, "Error: Access denied")
            self.assertFalse(outside_file.exists())
        finally:
            if outside_file.exists():
                outside_file.unlink()

    def test_read_file_legitimate(self):
        # Test legitimate read
        test_file = self.workspace_path / "test.txt"
        test_file.write_text("legitimate_data")

        result = tools.read_file("test.txt")
        self.assertEqual(result, "legitimate_data")

    def test_write_file_legitimate(self):
        # Test legitimate write
        result = tools.write_file("test2.txt", "legitimate_data")
        self.assertEqual(result, "File written: test2.txt")

        test_file = self.workspace_path / "test2.txt"
        self.assertTrue(test_file.exists())
        self.assertEqual(test_file.read_text(), "legitimate_data")

if __name__ == '__main__':
    unittest.main()
