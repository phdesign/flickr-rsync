# -*- coding: utf-8 -*-
import os, sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libs')
from mock import MagicMock, patch, call
import helpers
import modules.tree_walker
from modules.tree_walker import enumerate_peek, TreeWalker
from modules.file_info import FileInfo
from modules.folder_info import FolderInfo

class EnumeratePeekTest(unittest.TestCase):

    def test_should_return_empty_iterator_given_empty_iterator(self):
        mock_generator = iter(())
        was_called = False
        for x, has_next in enumerate_peek(mock_generator):
            was_called = True
        self.assertFalse(was_called, "Expected no enumeration of empty iterator")

    def test_has_next_should_return_true_given_more_items_exist(self):
        mock_generator = iter(range(2))
        x, has_next = next(enumerate_peek(mock_generator))
        self.assertTrue(has_next)

    def test_has_next_should_return_false_given_no_more_items_exist(self):
        mock_generator = iter(range(1))
        x, has_next = next(enumerate_peek(mock_generator))
        self.assertFalse(has_next)

    def test_should_iterate_over_all_items_given_iterator(self):
        mock_generator = iter(range(3))
        call_count = 0
        for x, has_next in enumerate_peek(mock_generator):
            call_count += 1
        self.assertEqual(call_count, 3)

    def test_should_iterate_over_all_items_given_list(self):
        my_list = [1,2,3]
        call_count = 0
        for x, has_next in enumerate_peek(my_list):
            call_count += 1
        self.assertEqual(call_count, 3)

class TreeWalkerTest(unittest.TestCase):

    def setUp(self):
        self.print_patch = patch('modules.tree_walker.print', create=True)
        self.mock_print = self.print_patch.start()
        self.time_patch = patch('modules.tree_walker.time.time', create=True)
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

    def test_should_print_wrapper_only_given_no_folders(self):
        walker = TreeWalker(self.config, self.storage)

        walker.walk()

        self.mock_print.assert_called_once_with("0 directories, 0 files read in 0.0 sec")

    def test_should_print_wrapper_only_given_empty_folders(self):
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': None, 'files': [] },
            { 'folder': self.folder_one, 'files': [] }
        ])

        walker.walk()

        self.mock_print.assert_called_once_with("0 directories, 0 files (excluding 1 empty directories) read in 0.0 sec")

    def test_should_print_root_files_given_root_files_enabled(self):
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': None, 'files': [self.file_one, self.file_two] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls([
            call(u"├─── A File".encode('utf-8')),
            call(u"└─── B File".encode('utf-8')),
            call("0 directories, 2 files read in 0.0 sec")
        ], any_order=False)
        self.assertEqual(self.mock_print.call_count, 3)

    @unittest.skip("Ligitimately broken, I just don't have a good fix for it")
    def test_should_not_print_connector_when_printing_root_files_given_folders_are_hidden(self):
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': None, 'files': [self.file_one, self.file_two] },
            { 'folder': self.folder_one, 'files': [] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls([
            call(u"├─── A File".encode('utf-8')),
            call(u"└─── B File".encode('utf-8')),
            call("0 directories, 2 files (excluding 1 empty directories) read in 0.0 sec")
        ], any_order=False)
        self.assertEqual(self.mock_print.call_count, 3)

    def test_should_not_print_root_files_given_root_files_disabled(self):
        self.config.root_files = False
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': None, 'files': [self.file_one, self.file_two] }
        ])

        walker.walk()

        self.mock_print.assert_called_once_with("0 directories, 0 files read in 0.0 sec")

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
        ], any_order=False)
        self.assertEqual(self.mock_print.call_count, 4)

    @unittest.skip("")
    def test_should_print_all_folders(self):
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.folder_one, 'files': [self.file_one] },
            { 'folder': self.folder_two, 'files': [self.file_two] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls([
            call("Folder, Filename, Checksum"),
            call("A Folder, A File, None"),
            call("B Folder, B File, None")
        ], any_order=False)
        self.assertEqual(self.mock_print.call_count, 3)

    @unittest.skip("")
    def test_should_print_checksum_given_file_has_checksum(self):
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.folder_one, 'files': [self.file_three] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls([
            call("Folder, Filename, Checksum"),
            call("A Folder, C File, abc123")
        ], any_order=False)
        self.assertEqual(self.mock_print.call_count, 2)

    @unittest.skip("")
    def test_should_sort_folders_and_files_given_sort_enabled(self):
        self.config.list_sort = True
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.folder_two, 'files': [self.file_three, self.file_two] },
            { 'folder': self.folder_one, 'files': [self.file_one] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls([
            call("Folder, Filename, Checksum"),
            call("A Folder, A File, None"),
            call("B Folder, B File, None"),
            call("B Folder, C File, abc123")
        ], any_order=False)
        self.assertEqual(self.mock_print.call_count, 4)

    @unittest.skip("")
    def test_should_not_sort_folders_and_files_given_sort_disabled(self):
        self.config.list_sort = False
        walker = TreeWalker(self.config, self.storage)
        helpers.setup_storage(self.storage, [
            { 'folder': self.folder_two, 'files': [self.file_three, self.file_two] },
            { 'folder': self.folder_one, 'files': [self.file_one] }
        ])

        walker.walk()

        self.mock_print.assert_has_calls([
            call("Folder, Filename, Checksum"),
            call("B Folder, C File, abc123"),
            call("B Folder, B File, None"),
            call("A Folder, A File, None")
        ], any_order=False)
        self.assertEqual(self.mock_print.call_count, 4)

if __name__ == '__main__':
    unittest.main(verbosity=2)
