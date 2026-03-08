import unittest
import tempfile
import shutil
from pathlib import Path
import myclaw.tools

class TestTools(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for the workspace
        self.test_workspace_dir = tempfile.mkdtemp()
        self.test_workspace = Path(self.test_workspace_dir).resolve()

        # Override the WORKSPACE variable in the tools module
        self.original_workspace = myclaw.tools.WORKSPACE
        myclaw.tools.WORKSPACE = self.test_workspace

    def tearDown(self):
        # Restore the original WORKSPACE variable
        myclaw.tools.WORKSPACE = self.original_workspace

        # Clean up the temporary directory
        shutil.rmtree(self.test_workspace_dir)

    def test_write_read_file_success(self):
        # Test writing and reading a file within the workspace
        write_result = myclaw.tools.write_file("test_file.txt", "hello world")
        self.assertEqual(write_result, "File written: test_file.txt")

        read_result = myclaw.tools.read_file("test_file.txt")
        self.assertEqual(read_result, "hello world")

    def test_read_file_path_traversal(self):
        # Create a sensitive file outside the workspace
        sensitive_dir = tempfile.mkdtemp()
        sensitive_file = Path(sensitive_dir) / "passwd"
        sensitive_file.write_text("secret")

        try:
            # Attempt to read the sensitive file using path traversal
            # calculate relative path
            import os
            rel_path = os.path.relpath(sensitive_file, self.test_workspace)
            read_result = myclaw.tools.read_file(rel_path)
            self.assertEqual(read_result, "Error: Access denied")

            # Attempt to read using absolute path
            read_result_abs = myclaw.tools.read_file(str(sensitive_file))
            self.assertEqual(read_result_abs, "Error: Access denied")
        finally:
            shutil.rmtree(sensitive_dir)

    def test_write_file_path_traversal(self):
        # Attempt to write outside the workspace
        write_result = myclaw.tools.write_file("../outside.txt", "malicious")
        self.assertEqual(write_result, "Error: Access denied")

        # Verify the file was not written outside the workspace
        self.assertFalse((self.test_workspace / "../outside.txt").resolve().exists())

        # Attempt to write using absolute path
        abs_target = Path(self.test_workspace_dir).parent / "abs_outside.txt"
        write_result_abs = myclaw.tools.write_file(str(abs_target), "malicious")
        self.assertEqual(write_result_abs, "Error: Access denied")
        self.assertFalse(abs_target.exists())

if __name__ == '__main__':
    unittest.main()
