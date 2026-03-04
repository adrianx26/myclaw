import unittest
from unittest.mock import patch
import sys
import io

import cli

class TestCLI(unittest.TestCase):
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('cli.load_config')
    @patch('sys.argv', ['cli.py', 'unknown'])
    def test_unknown_command(self, mock_load_config, mock_stdout):
        # We need to mock load_config so it doesn't try to read config.json
        mock_load_config.return_value = {}

        cli.main()

        self.assertIn("Comandă necunoscută", mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()
