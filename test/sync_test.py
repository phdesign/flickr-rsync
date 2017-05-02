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
        self.config.dry_run = False
        self.src_storage = MagicMock()
        self.dest_storage = MagicMock()
        self.folder_one = FolderInfo(id=1, name='A')
        self.folder_two = FolderInfo(id=2, name='B')
        self.folder_three = FolderInfo(id=3, name='C')
        self.folder_four = FolderInfo(id=4, name='D')
        self.sync = Sync(self.config, self.src_storage, self.dest_storage)

class SyncCopyTest(SyncTest):

    def setUp(self):
        super(SyncCopyTest, self).setUp()
        self.mock = MagicMock()
        self.sync._copy_folder = self.mock

    def test_should_copy_folder_for_each_missing_folder_in_src(self):
        self.src_storage.list_folders.return_value = [self.folder_one, self.folder_two, self.folder_three]
        self.dest_storage.list_folders.return_value = []

        self.sync.run()

        self.mock.assert_any_call(self.folder_one)
        self.mock.assert_any_call(self.folder_two)
        self.mock.assert_any_call(self.folder_three)
        self.assertEqual(self.mock.call_count, 3)

    def test_should_copy_folder_for_each_missing_folder_given_some_exist_already(self):
        self.src_storage.list_folders.return_value = [self.folder_one, self.folder_two, self.folder_three, self.folder_four]
        self.dest_storage.list_folders.return_value = [self.folder_four, self.folder_three]

        self.sync.run()

        self.mock.assert_any_call(self.folder_one)
        self.mock.assert_any_call(self.folder_two)
        self.assertEqual(self.mock.call_count, 2)

    def test_should_not_copy_folder_given_all_exist_already(self):
        self.src_storage.list_folders.return_value = [self.folder_one, self.folder_two]
        self.dest_storage.list_folders.return_value = [self.folder_two, self.folder_one]

        self.sync.run()

        self.mock.assert_not_called()

class SyncMergeTest(SyncTest):

    def setUp(self):
        super(SyncMergeTest, self).setUp()
        self.file_one = FileInfo(id=1, name='A')
        self.file_two = FileInfo(id=1, name='B')
        self.mock = MagicMock()
        self.src_storage.copy_file = self.mock

    def test_should_copy_missing_files_in_existing_folder(self):
        self.src_storage.list_folders.return_value = [self.folder_one]
        self.dest_storage.list_folders.return_value = [self.folder_one]
        self.src_storage.list_files.return_value = [self.file_one, self.file_two]
        self.dest_storage.list_files.return_value = []

        self.sync.run()
        
        self.mock.assert_any_call(self.file_one, self.folder_one.name, self.dest_storage)
        self.mock.assert_any_call(self.file_two, self.folder_one.name, self.dest_storage)
        self.assertEqual(self.mock.call_count, 2)

    def test_should_copy_missing_files_from_all_folders(self):
        self.src_storage.list_folders.return_value = [self.folder_one, self.folder_two]
        self.dest_storage.list_folders.return_value = [self.folder_one, self.folder_two]
        self.src_storage.list_files.side_effect = lambda x: [self.file_one] if x == self.folder_one else [self.file_two]
        self.dest_storage.list_files.return_value = []

        self.sync.run()
        
        self.mock.assert_any_call(self.file_one, self.folder_one.name, self.dest_storage)
        self.mock.assert_any_call(self.file_two, self.folder_two.name, self.dest_storage)
        self.assertEqual(self.mock.call_count, 2)

    def test_should_copy_missing_files_in_existing_folder_given_files_exist(self):
        self.src_storage.list_folders.return_value = [self.folder_one]
        self.dest_storage.list_folders.return_value = [self.folder_one]
        self.src_storage.list_files.return_value = [self.file_one, self.file_two]
        self.dest_storage.list_files.return_value = [self.file_two]

        self.sync.run()
        
        self.mock.assert_any_call(self.file_one, self.folder_one.name, self.dest_storage)
        self.assertEqual(self.mock.call_count, 1)

    def test_should_not_copy_files_given_all_files_exist(self):
        self.src_storage.list_folders.return_value = [self.folder_one]
        self.dest_storage.list_folders.return_value = [self.folder_one]
        self.src_storage.list_files.return_value = [self.file_one]
        self.dest_storage.list_files.return_value = [self.file_one, self.file_two]

        self.sync.run()
        
        self.mock.assert_not_called()

if __name__ == '__main__':
    unittest.main(verbosity=2)
