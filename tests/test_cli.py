import unittest
from unittest.mock import patch
import sys
import argparse
from fs_manager import cli

class TestCLI(unittest.TestCase):
    
    @patch('fs_manager.core.operations.copy_file')
    def test_cli_copy(self, mock_copy):
        test_args = ["fs-manager", "copy", "src.txt", "dst.txt"]
        with patch.object(sys, 'argv', test_args):
            cli.main()
        mock_copy.assert_called_once_with("src.txt", "dst.txt")

    @patch('fs_manager.core.operations.delete_item')
    def test_cli_delete(self, mock_delete):
        test_args = ["fs-manager", "delete", "folder1"]
        with patch.object(sys, 'argv', test_args):
            cli.main()
        mock_delete.assert_called_once_with("folder1")
        
    @patch('fs_manager.core.operations.add_date')
    def test_cli_add_date_recursive(self, mock_add_date):
        test_args = ["fs-manager", "add-date", "folder1", "--recursive"]
        with patch.object(sys, 'argv', test_args):
            cli.main()
        mock_add_date.assert_called_once_with("folder1", True)

if __name__ == '__main__':
    unittest.main()