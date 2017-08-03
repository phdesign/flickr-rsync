import os, sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libs')
from mock import MagicMock, patch, call
import helpers
import flickr_rsync.rx_sync
from flickr_rsync.rx_sync import RxSync
from flickr_rsync.file_info import FileInfo
from flickr_rsync.folder_info import FolderInfo
from flickr_rsync.root_folder_info import RootFolderInfo

class SyncTestBase(unittest.TestCase):

    def setUp(self):
        self.print_patch = patch('flickr_rsync.rx_sync.print')
        self.mock_print = self.print_patch.start()
        self.vprint_patch = patch('flickr_rsync.rx_sync.vprint', create=True)
        self.mock_vprint = self.vprint_patch.start()

        self.config = MagicMock()
        self.config.dry_run = False
        self.src_storage = MagicMock()
        self.dest_storage = MagicMock()
        self.folder_one = FolderInfo(id=1, name='A')
        self.folder_two = FolderInfo(id=2, name='B')
        self.folder_three = FolderInfo(id=3, name='C')
        self.folder_four = FolderInfo(id=4, name='D')
        self.root_folder = RootFolderInfo()
        self.file_one = FileInfo(id=1, name='A')
        self.file_two = FileInfo(id=1, name='B')

        self.sync = RxSync(self.config, self.src_storage, self.dest_storage)
        self.mock = MagicMock()
        self.src_storage.copy_file = self.mock

    def tearDown(self):
        self.print_patch.stop()
        self.vprint_patch.stop()

class SyncTest(SyncTestBase):

    def test_should_not_copy_anything_given_dry_run_enabled(self):
        self.config.dry_run = True
        helpers.setup_storage(self.src_storage, [
            { 'folder': self.folder_one, 'files': [self.file_one] },
            { 'folder': self.folder_two, 'files': [self.file_one, self.file_two] }
        ])
        helpers.setup_storage(self.dest_storage, [
            { 'folder': self.folder_two, 'files': [self.file_one] }
        ])

        self.sync.run()

        self.mock.assert_not_called()

# @unittest.skip("")
class SyncCopyTest(SyncTestBase):

    def setUp(self):
        super(SyncCopyTest, self).setUp()

    def test_should_copy_folder_for_each_missing_folder_in_src(self):
        helpers.setup_storage(self.src_storage, [
            { 'folder': self.folder_one, 'files': [self.file_one] },
            { 'folder': self.folder_two, 'files': [self.file_one] },
            { 'folder': self.folder_three, 'files': [self.file_one] },
        ])
        helpers.setup_storage(self.dest_storage, [])

        self.sync.run()

        self.mock.assert_has_calls_exactly([
            call(self.file_one, self.folder_one.name, self.dest_storage),
            call(self.file_one, self.folder_two.name, self.dest_storage),
            call(self.file_one, self.folder_three.name, self.dest_storage)
        ], any_order=True)

    def test_should_copy_folder_for_each_missing_folder_given_some_exist_already(self):
        helpers.setup_storage(self.src_storage, [
            { 'folder': self.folder_one, 'files': [self.file_one] },
            { 'folder': self.folder_two, 'files': [self.file_one] },
            { 'folder': self.folder_three, 'files': [self.file_one] },
            { 'folder': self.folder_four, 'files': [self.file_one] },
        ])
        helpers.setup_storage(self.dest_storage, [
            { 'folder': self.folder_four, 'files': [self.file_one] },
            { 'folder': self.folder_three, 'files': [self.file_one] }
        ])

        self.sync.run()

        self.mock.assert_has_calls_exactly([
            call(self.file_one, self.folder_one.name, self.dest_storage),
            call(self.file_one, self.folder_two.name, self.dest_storage)
        ], any_order=True)

    def test_should_not_copy_folder_given_all_exist_already(self):
        helpers.setup_storage(self.src_storage, [
            { 'folder': self.folder_one, 'files': [self.file_one] },
            { 'folder': self.folder_two, 'files': [self.file_one] }
        ])
        helpers.setup_storage(self.dest_storage, [
            { 'folder': self.folder_two, 'files': [self.file_one] },
            { 'folder': self.folder_one, 'files': [self.file_one] }
        ])

        self.sync.run()

        self.mock.assert_not_called()

class SyncMergeTest(SyncTestBase):

    def setUp(self):
        super(SyncMergeTest, self).setUp()

    def test_should_copy_missing_files_in_existing_folder(self):
        helpers.setup_storage(self.src_storage, [{
            'folder': self.folder_one,
            'files': [self.file_one, self.file_two]
        }])
        helpers.setup_storage(self.dest_storage, [{
            'folder': self.folder_one,
            'files': []
        }])

        self.sync.run()
        
        self.mock.assert_has_calls_exactly([
            call(self.file_one, self.folder_one.name, self.dest_storage),
            call(self.file_two, self.folder_one.name, self.dest_storage)
        ], any_order=True)

    def test_should_copy_missing_files_from_all_folders(self):
        helpers.setup_storage(self.src_storage, [
            { 'folder': self.folder_one, 'files': [self.file_one] },
            { 'folder': self.folder_two, 'files': [self.file_two] }
        ])
        helpers.setup_storage(self.dest_storage, [
            { 'folder': self.folder_one, 'files': [] },
            { 'folder': self.folder_two, 'files': [] }
        ])

        self.sync.run()
        
        self.mock.assert_has_calls_exactly([
            call(self.file_one, self.folder_one.name, self.dest_storage),
            call(self.file_two, self.folder_two.name, self.dest_storage)
        ], any_order=True)

    def test_should_copy_missing_files_in_existing_folder_given_files_exist(self):
        helpers.setup_storage(self.src_storage, [{
            'folder': self.folder_one,
            'files': [self.file_one, self.file_two]
        }])
        helpers.setup_storage(self.dest_storage, [{
            'folder': self.folder_one,
            'files': [self.file_two]
        }])

        self.sync.run()
        
        self.mock.assert_called_once_with(self.file_one, self.folder_one.name, self.dest_storage)

    def test_should_not_copy_files_given_all_files_exist(self):
        helpers.setup_storage(self.src_storage, [{
            'folder': self.folder_one,
            'files': [self.file_one]
        }])
        helpers.setup_storage(self.dest_storage, [{
            'folder': self.folder_one,
            'files': [self.file_one, self.file_two]
        }])

        self.sync.run()
        
        self.mock.assert_not_called()

    def test_should_merge_files_in_root_folder_given_root_files_enabled(self):
        self.config.root_files = True
        helpers.setup_storage(self.src_storage, [
            { 'folder': self.root_folder, 'files': [self.file_one, self.file_two] },
        ])
        helpers.setup_storage(self.dest_storage, [
            { 'folder': self.root_folder, 'files': [self.file_two] },
        ])

        self.sync.run()

        self.mock.assert_has_calls_exactly([
            call(self.file_one, '', self.dest_storage),
        ], any_order=True)

if __name__ == '__main__':
    unittest.main(verbosity=2)
