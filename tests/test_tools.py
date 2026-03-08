import unittest
import tempfile
import shutil
from pathlib import Path
import myclaw.tools

class TestTools(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.workspace_path = Path(self.test_dir)

        # Override WORKSPACE in tools
        self.original_workspace = myclaw.tools.WORKSPACE
        myclaw.tools.WORKSPACE = self.workspace_path

    def tearDown(self):
        # Restore original WORKSPACE
        myclaw.tools.WORKSPACE = self.original_workspace
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_read_file_success(self):
        # Setup: Create a file in the mock workspace
        test_file = self.workspace_path / "hello.txt"
        test_file.write_text("Hello World!")

        # Action
        result = myclaw.tools.read_file("hello.txt")

        # Assertion
        self.assertEqual(result, "Hello World!")

    def test_write_file_success(self):
        # Action
        result = myclaw.tools.write_file("new_file.txt", "New Content")

        # Assertion
        self.assertEqual(result, "File written: new_file.txt")
        test_file = self.workspace_path / "new_file.txt"
        self.assertTrue(test_file.exists())
        self.assertEqual(test_file.read_text(), "New Content")

    def test_read_file_path_traversal(self):
        # Action: Attempt to read a file outside workspace
        result = myclaw.tools.read_file("../../../etc/passwd")

        # Assertion: Should be denied
        self.assertEqual(result, "Error: Access denied")

    def test_write_file_path_traversal(self):
        # Action: Attempt to write a file outside workspace
        result = myclaw.tools.write_file("../../../etc/passwd", "Hacked")

        # Assertion: Should be denied
        self.assertEqual(result, "Error: Access denied")

    def test_read_file_absolute_path_outside(self):
        # Action: Attempt to read a file via absolute path outside workspace
        result = myclaw.tools.read_file("/etc/passwd")

        # Assertion: Should be denied
        self.assertEqual(result, "Error: Access denied")

    def test_write_file_absolute_path_outside(self):
        # Action: Attempt to write a file via absolute path outside workspace
        result = myclaw.tools.write_file("/etc/passwd", "Hacked")

        # Assertion: Should be denied
        self.assertEqual(result, "Error: Access denied")

if __name__ == '__main__':
    unittest.main()
