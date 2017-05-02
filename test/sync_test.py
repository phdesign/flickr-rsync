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
        self.file_one = FileInfo(id=1, name='A')
        self.file_two = FileInfo(id=1, name='B')

        self.sync = Sync(self.config, self.src_storage, self.dest_storage)
        self.mock = MagicMock()
        self.src_storage.copy_file = self.mock

    def _setup_storage(self, storage, folders):
        storage.list_folders.return_value = [x['folder'] for x in folders]
        storage.list_files.side_effect = lambda folder: next(x['files'] for x in folders if x['folder'] == folder)

# @unittest.skip("")
class SyncCopyTest(SyncTest):

    def setUp(self):
        super(SyncCopyTest, self).setUp()

    def test_should_copy_folder_for_each_missing_folder_in_src(self):
        self._setup_storage(self.src_storage, [
            { 'folder': self.folder_one, 'files': [self.file_one] },
            { 'folder': self.folder_two, 'files': [self.file_one] },
            { 'folder': self.folder_three, 'files': [self.file_one] },
        ])
        self._setup_storage(self.dest_storage, [])

        self.sync.run()

        self.mock.assert_any_call(self.file_one, self.folder_one.name, self.dest_storage)
        self.mock.assert_any_call(self.file_one, self.folder_two.name, self.dest_storage)
        self.mock.assert_any_call(self.file_one, self.folder_three.name, self.dest_storage)
        self.assertEqual(self.mock.call_count, 3)

    def test_should_copy_folder_for_each_missing_folder_given_some_exist_already(self):
        self._setup_storage(self.src_storage, [
            { 'folder': self.folder_one, 'files': [self.file_one] },
            { 'folder': self.folder_two, 'files': [self.file_one] },
            { 'folder': self.folder_three, 'files': [self.file_one] },
            { 'folder': self.folder_four, 'files': [self.file_one] },
        ])
        self._setup_storage(self.dest_storage, [
            { 'folder': self.folder_four, 'files': [self.file_one] },
            { 'folder': self.folder_three, 'files': [self.file_one] }
        ])

        self.sync.run()

        self.mock.assert_any_call(self.file_one, self.folder_one.name, self.dest_storage)
        self.mock.assert_any_call(self.file_one, self.folder_two.name, self.dest_storage)
        self.assertEqual(self.mock.call_count, 2)

    def test_should_not_copy_folder_given_all_exist_already(self):
        self._setup_storage(self.src_storage, [
            { 'folder': self.folder_one, 'files': [self.file_one] },
            { 'folder': self.folder_two, 'files': [self.file_one] }
        ])
        self._setup_storage(self.dest_storage, [
            { 'folder': self.folder_two, 'files': [self.file_one] },
            { 'folder': self.folder_one, 'files': [self.file_one] }
        ])

        self.sync.run()

        self.mock.assert_not_called()

class SyncMergeTest(SyncTest):

    def setUp(self):
        super(SyncMergeTest, self).setUp()

    def test_should_copy_missing_files_in_existing_folder(self):
        self._setup_storage(self.src_storage, [{
            'folder': self.folder_one,
            'files': [self.file_one, self.file_two]
        }])
        self._setup_storage(self.dest_storage, [{
            'folder': self.folder_one,
            'files': []
        }])

        self.sync.run()
        
        self.mock.assert_any_call(self.file_one, self.folder_one.name, self.dest_storage)
        self.mock.assert_any_call(self.file_two, self.folder_one.name, self.dest_storage)
        self.assertEqual(self.mock.call_count, 2)

    def test_should_copy_missing_files_from_all_folders(self):
        self._setup_storage(self.src_storage, [
            { 'folder': self.folder_one, 'files': [self.file_one] },
            { 'folder': self.folder_two, 'files': [self.file_two] }
        ])
        self._setup_storage(self.dest_storage, [
            { 'folder': self.folder_one, 'files': [] },
            { 'folder': self.folder_two, 'files': [] }
        ])

        self.sync.run()
        
        self.mock.assert_any_call(self.file_one, self.folder_one.name, self.dest_storage)
        self.mock.assert_any_call(self.file_two, self.folder_two.name, self.dest_storage)
        self.assertEqual(self.mock.call_count, 2)

    def test_should_copy_missing_files_in_existing_folder_given_files_exist(self):
        self._setup_storage(self.src_storage, [{
            'folder': self.folder_one,
            'files': [self.file_one, self.file_two]
        }])
        self._setup_storage(self.dest_storage, [{
            'folder': self.folder_one,
            'files': [self.file_two]
        }])

        self.sync.run()
        
        self.mock.assert_any_call(self.file_one, self.folder_one.name, self.dest_storage)
        self.assertEqual(self.mock.call_count, 1)

    def test_should_not_copy_files_given_all_files_exist(self):
        self._setup_storage(self.src_storage, [{
            'folder': self.folder_one,
            'files': [self.file_one]
        }])
        self._setup_storage(self.dest_storage, [{
            'folder': self.folder_one,
            'files': [self.file_one, self.file_two]
        }])

        self.sync.run()
        
        self.mock.assert_not_called()

if __name__ == '__main__':
    unittest.main(verbosity=2)
