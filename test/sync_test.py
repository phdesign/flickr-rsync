import os, sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libs')
from mock import MagicMock
from modules.sync import Sync
from modules.file_info import FileInfo
from modules.folder_info import FolderInfo

class SyncTest(unittest.TestCase):

    def setUp(self):
        self.config = MagicMock()
        self.src_storage = MagicMock()
        self.dest_storage = MagicMock()
        self.sync = Sync(self.config, self.src_storage, self.dest_storage)
        self.folder_one = FolderInfo(id=1, name='A')
        self.folder_two = FolderInfo(id=2, name='B')
        self.folder_three = FolderInfo(id=3, name='C')
        self.folder_four = FolderInfo(id=4, name='D')

    def test_should_copy_folder_for_each_missing_folder_in_src(self):
        self.src_storage.list_folders.return_value = [self.folder_one, self.folder_two, self.folder_three]
        self.dest_storage.list_folders.return_value = []

        mock = MagicMock()
        self.sync._copy_folder = mock
        self.sync.run()

        mock.assert_any_call(self.folder_one)
        mock.assert_any_call(self.folder_two)
        mock.assert_any_call(self.folder_three)
        self.assertEqual(mock.call_count, 3)

    def test_should_copy_folder_for_each_missing_folder_given_some_exist_already(self):
        self.src_storage.list_folders.return_value = [self.folder_one, self.folder_two, self.folder_three, self.folder_four]
        self.dest_storage.list_folders.return_value = [self.folder_four, self.folder_three]

        mock = MagicMock()
        self.sync._copy_folder = mock
        self.sync.run()

        mock.assert_any_call(self.folder_one)
        mock.assert_any_call(self.folder_two)
        self.assertEqual(mock.call_count, 2)

    def test_should_not_call_copy_folder_given_all_exist_already(self):
        self.src_storage.list_folders.return_value = [self.folder_one, self.folder_two]
        self.dest_storage.list_folders.return_value = [self.folder_two, self.folder_one]

        mock = MagicMock()
        self.sync._copy_folder = mock
        self.sync.run()

        mock.assert_not_called()

    def test_should_copy_missing_files_in_existing_folder(self):
        self.src_storage.list_folders.return_value = [self.folder_one]
        self.dest_storage.list_folders.return_value = [self.folder_one]
        file_one = FileInfo(id=1, name='A')
        file_two = FileInfo(id=1, name='B')
        # self.src_storage.list_files.side_effect = lambda x: [file_one, file_two] if x == self.folder_one else []
        self.src_storage.list_files.return_value = [file_one, file_two]
        self.dest_storage.list_files.return_value = []
        mock = MagicMock()
        self.src_storage.copy_file = mock

        self.sync.run()
        
        mock.assert_any_call(file_one, self.folder_one.name, self.dest_storage)
        mock.assert_any_call(file_one, self.folder_one.name, self.dest_storage)
        self.assertEqual(mock.call_count, 2)

if __name__ == '__main__':
    unittest.main(verbosity=2)
