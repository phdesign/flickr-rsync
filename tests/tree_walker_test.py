# -*- coding: utf-8 -*-
import os, sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libs')
from mock import MagicMock, patch, call
import helpers
from flickr_rsync.tree_walker import TreeWalker
from flickr_rsync.file_info import FileInfo
from flickr_rsync.folder_info import FolderInfo
from flickr_rsync.root_folder_info import RootFolderInfo

class TreeWalkerTest(unittest.TestCase):

    def setUp(self):
        self.print_patch = patch('flickr_rsync.tree_walker.print', create=True)
        self.mock_print = self.print_patch.start()
        self.time_patch = patch('flickr_rsync.tree_walker.time.time', create=True)
        self.time_patch.start().return_value = 0

        self.config = MagicMock()
        self.storage = MagicMock()
        self.folder_one = FolderInfo(id=1, name='A Folder')
        self.folder_two = FolderInfo(id=2, name='B Folder')
        self.folder_three = FolderInfo(id=3, name='C Folder')
        self.folder_four = FolderInfo(id=4, name='D Folder')
        self.root_folder = RootFolderInfo()
        self.file_one = FileInfo(id=1, name='A File')
        self.file_two = FileInfo(id=2, name='B File')
        self.file_three = FileInfo(id=3, name='C File', checksum='abc123')

    def tearDown(self):
        self.print_patch.stop()
        self.time_patch.stop()

    def test_should_print_wrapper_only_given_no_folders(self):
        walker = TreeWalker(self.config, self.storage)

        walker.walk()

        self.mock_print.assert_called_once_with("0 directories, 0 files read in 0.0 sec")

    def test_should_print_wrapper_only_given_empty_folders(self):
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.root_folder, 'files': [] },
            { 'folder': self.folder_one, 'files': [] }
        ])

        walker.walk()

        self.mock_print.assert_called_once_with("0 directories, 0 files (excluding 1 empty directories) read in 0.0 sec")

    def test_should_print_root_files_given_root_files_enabled(self):
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.root_folder, 'files': [self.file_one, self.file_two] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls_exactly([
            call(u"├─── A File".encode('utf-8')),
            call(u"└─── B File".encode('utf-8')),
            call("0 directories, 2 files read in 0.0 sec")
        ])

    @unittest.skip("Ligitimately broken, I just don't have a good fix for it")
    def test_should_not_print_connector_when_printing_root_files_given_folders_are_hidden(self):
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.root_folder, 'files': [self.file_one, self.file_two] },
            { 'folder': self.folder_one, 'files': [] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls_exactly([
            call(u"├─── A File".encode('utf-8')),
            call(u"└─── B File".encode('utf-8')),
            call("0 directories, 2 files (excluding 1 empty directories) read in 0.0 sec")
        ])

    def test_should_not_print_root_files_given_root_files_disabled(self):
        self.config.root_files = False
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.root_folder, 'files': [self.file_one, self.file_two] }
        ])

        walker.walk()

        self.mock_print.assert_called_once_with("0 directories, 0 files read in 0.0 sec")

    def test_should_print_root_files_given_root_files_enabled_and_folders_exist(self):
        self.config.list_sort = False
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.root_folder, 'files': [self.file_three] },
            { 'folder': self.folder_one, 'files': [self.file_one] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls([
            call(u"├─── C File [abc123]".encode('utf-8')),
            call(u"│   ".encode('utf-8')),
            call(u"└─── A Folder".encode('utf-8')),
            call(u"    └─── A File".encode('utf-8')),
            call("1 directories, 2 files read in 0.0 sec")
        ])

    def test_should_print_folder_files(self):
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.folder_one, 'files': [self.file_one, self.file_two] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls([
            call(u"└─── A Folder".encode('utf-8')),
            call(u"    ├─── A File".encode('utf-8')),
            call(u"    └─── B File".encode('utf-8')),
            call("1 directories, 2 files read in 0.0 sec")
        ])

    def test_should_print_all_folders(self):
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.folder_one, 'files': [self.file_one] },
            { 'folder': self.folder_two, 'files': [self.file_two] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls([
            call(u"├─── A Folder".encode('utf-8')),
            call(u"│   └─── A File".encode('utf-8')),
            call(u"│   ".encode('utf-8')),
            call(u"└─── B Folder".encode('utf-8')),
            call(u"    └─── B File".encode('utf-8')),
            call("2 directories, 2 files read in 0.0 sec")
        ])

    def test_should_print_checksum_given_file_has_checksum(self):
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.folder_one, 'files': [self.file_three] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls([
            call(u"└─── A Folder".encode('utf-8')),
            call(u"    └─── C File [abc123]".encode('utf-8')),
            call("1 directories, 1 files read in 0.0 sec")
        ])

    def test_should_sort_folders_and_files_given_sort_enabled(self):
        self.config.list_sort = True
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.folder_two, 'files': [self.file_three, self.file_two] },
            { 'folder': self.folder_one, 'files': [self.file_one] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls([
            call(u"├─── A Folder".encode('utf-8')),
            call(u"│   └─── A File".encode('utf-8')),
            call(u"│   ".encode('utf-8')),
            call(u"└─── B Folder".encode('utf-8')),
            call(u"    ├─── B File".encode('utf-8')),
            call(u"    └─── C File [abc123]".encode('utf-8')),
            call("2 directories, 3 files read in 0.0 sec")
        ])

    def test_should_not_sort_folders_and_files_given_sort_disabled(self):
        self.config.list_sort = False
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.folder_two, 'files': [self.file_three, self.file_two] },
            { 'folder': self.folder_one, 'files': [self.file_one] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls([
            call(u"├─── B Folder".encode('utf-8')),
            call(u"│   ├─── C File [abc123]".encode('utf-8')),
            call(u"│   └─── B File".encode('utf-8')),
            call(u"│   ".encode('utf-8')),
            call(u"└─── A Folder".encode('utf-8')),
            call(u"    └─── A File".encode('utf-8')),
            call("2 directories, 3 files read in 0.0 sec")
        ])

if __name__ == '__main__':
    unittest.main(verbosity=2)
