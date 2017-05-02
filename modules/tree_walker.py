# -*- coding: utf-8 -*-

import operator
from walker import Walker

UNICODE_LEAF = u"├─── ".encode('utf-8')
UNICODE_LAST_LEAF = u"└─── ".encode('utf-8')
UNICODE_BRANCH = u"│   ".encode('utf-8')
UNICODE_LAST_BRANCH = "    "

class TreeWalker(Walker):
    
    def __init__(self, config, storage):
        self._config = config
        self._storage = storage
        self._file_count = 0
        self._hidden_folder_count = 0
        self._folder_count = 0

    def walk(self):
        folders = sorted(self._storage.list_folders(), key=lambda x: x.name)
        if self._config.root_files:
            self._print_root_files(len(folders) > 0)
        self._print_folders(folders)
        print "{} directories, {} files{}".format(self._folder_count, self._file_count,
                " (excluding {} empty directories)".format(self._hidden_folder_count) if self._hidden_folder_count > 0 else "")

    def _print_root_files(self, has_folders):
        files = sorted(self._storage.list_files(None), key=lambda x: x.name)
        if len(files) == 0:
            return;
        self._file_count += len(files)
        last = len(files) - 1
        for i, x in enumerate(files):
            print self._format_leaf(
                "{} [{:.6}]".format(x.name.encode('utf-8'), x.checksum) if x.checksum else x.name.encode('utf-8'), 
                i == last and not has_folders)
        if has_folders:
            print UNICODE_BRANCH

    def _print_folders(self, folders):
        last = len(folders) - 1
        for i, x in enumerate(folders):
            self._print_folder(x, i == last) 

    def _print_folder(self, folder, is_last):
        files = sorted(self._storage.list_files(folder), key=lambda x: x.name)
        if len(files) == 0:
            self._hidden_folder_count += 1
            return
        print self._format_leaf(folder.name.encode('utf-8'), is_last)
        self._folder_count += 1
        self._file_count += len(files)
        prefix = UNICODE_LAST_BRANCH if is_last else UNICODE_BRANCH
        self._print_files(prefix, files)
        if not is_last:
            print UNICODE_BRANCH
    
    def _print_files(self, prefix, files):
        last = len(files) - 1
        for i, x in enumerate(files):
            print prefix + self._format_leaf(
                "{} [{:.6}]".format(x.name.encode('utf-8'), x.checksum) if x.checksum else x.name.encode('utf-8'), 
                i == last)

    def _format_leaf(self, text, is_last):
        return (UNICODE_LAST_LEAF if is_last else UNICODE_LEAF) + text
