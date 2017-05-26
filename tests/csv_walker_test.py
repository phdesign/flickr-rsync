import os, sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
from mock import MagicMock, patch, call
import helpers
from flickr_rsync.csv_walker import CsvWalker
from flickr_rsync.file_info import FileInfo
from flickr_rsync.folder_info import FolderInfo

class CsvWalkerTest(unittest.TestCase):

    def setUp(self):
        self.print_patch = patch('flickr_rsync.csv_walker.print', create=True)
        self.mock_print = self.print_patch.start()
        self.time_patch = patch('flickr_rsync.tree_walker.time.time', create=True)
        self.time_patch.start().return_value = 0

        self.config = MagicMock()
        self.storage = MagicMock()
        self.folder_one = FolderInfo(id=1, name='A Folder')
        self.folder_two = FolderInfo(id=2, name='B Folder')
        self.folder_three = FolderInfo(id=3, name='C Folder')
        self.folder_four = FolderInfo(id=4, name='D Folder')
        self.file_one = FileInfo(id=1, name='A File')
        self.file_two = FileInfo(id=2, name='B File')
        self.file_three = FileInfo(id=3, name='C File', checksum='abc123')

    def tearDown(self):
        self.print_patch.stop()
        self.time_patch.stop()

    def test_should_print_header_only_given_no_folders(self):
        walker = CsvWalker(self.config, self.storage)

        walker.walk()

        self.mock_print.assert_has_calls_exactly([
            call("Folder, Filename, Checksum"),
            call("\ndone in 0.0 sec")
        ])

    def test_should_print_header_only_given_empty_folders(self):
        walker = CsvWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': None, 'files': [] },
            { 'folder': self.folder_one, 'files': [] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls_exactly([
            call("Folder, Filename, Checksum"),
            call("\ndone in 0.0 sec")
        ])

    def test_should_print_root_files_given_root_files_enabled(self):
        walker = CsvWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': None, 'files': [self.file_one, self.file_two] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls_exactly([
            call("Folder, Filename, Checksum"),
            call(", A File, None"),
            call(", B File, None"),
            call("\ndone in 0.0 sec")
        ])

    def test_should_not_print_root_files_given_root_files_disabled(self):
        self.config.root_files = False
        walker = CsvWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': None, 'files': [self.file_one, self.file_two] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls_exactly([
            call("Folder, Filename, Checksum"),
            call("\ndone in 0.0 sec")
        ])

    def test_should_print_folder_files(self):
        walker = CsvWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.folder_one, 'files': [self.file_one, self.file_two] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls_exactly([
            call("Folder, Filename, Checksum"),
            call("A Folder, A File, None"),
            call("A Folder, B File, None"),
            call("\ndone in 0.0 sec")
        ])

    def test_should_print_all_folders(self):
        walker = CsvWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.folder_one, 'files': [self.file_one] },
            { 'folder': self.folder_two, 'files': [self.file_two] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls_exactly([
            call("Folder, Filename, Checksum"),
            call("A Folder, A File, None"),
            call("B Folder, B File, None"),
            call("\ndone in 0.0 sec")
        ])

    def test_should_print_checksum_given_file_has_checksum(self):
        walker = CsvWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.folder_one, 'files': [self.file_three] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls_exactly([
            call("Folder, Filename, Checksum"),
            call("A Folder, C File, abc123"),
            call("\ndone in 0.0 sec")
        ])

    def test_should_sort_folders_and_files_given_sort_enabled(self):
        self.config.list_sort = True
        walker = CsvWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.folder_two, 'files': [self.file_three, self.file_two] },
            { 'folder': self.folder_one, 'files': [self.file_one] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls_exactly([
            call("Folder, Filename, Checksum"),
            call("A Folder, A File, None"),
            call("B Folder, B File, None"),
            call("B Folder, C File, abc123"),
            call("\ndone in 0.0 sec")
        ])

    def test_should_not_sort_folders_and_files_given_sort_disabled(self):
        self.config.list_sort = False
        walker = CsvWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.folder_two, 'files': [self.file_three, self.file_two] },
            { 'folder': self.folder_one, 'files': [self.file_one] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls_exactly([
            call("Folder, Filename, Checksum"),
            call("B Folder, C File, abc123"),
            call("B Folder, B File, None"),
            call("A Folder, A File, None"),
            call("\ndone in 0.0 sec")
        ])

# if __name__ == '__main__':
    # unittest.main(verbosity=2)

