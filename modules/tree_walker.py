# -*- coding: utf-8 -*-

import operator

UNICODE_LEAF = u"├─── ".encode('utf-8')
UNICODE_LAST_LEAF = u"└─── ".encode('utf-8')
UNICODE_BRANCH = u"│   ".encode('utf-8')
UNICODE_LAST_BRANCH = "    "

class TreeWalker(object):
    
    def __init__(self, storage):
        self._storage = storage
        self._file_count = 0
        self._hidden_folder_count = 0
        self._folder_count = 0

    def walk(self):
        folders = self._storage.list_folders()
        self.print_folders(folders)
        print "{} directories, {} files{}".format(self._folder_count, self._file_count,
                " (excluding {} empty directories)".format(self._hidden_folder_count) if self._hidden_folder_count > 0 else "")

    def print_folders(self, folders):
        last = len(folders) - 1
        sorted(folders, key=lambda x: x.name)
        for i, x in enumerate(folders):
            self.print_folder(x, i == last) 

    def print_folder(self, folder, is_last):
        files = self._storage.list_files(folder)
        if len(files) == 0:
            self._hidden_folder_count += 1
            return
        print self.format_leaf(folder.name.encode('utf-8'), is_last)
        self._folder_count += 1
        self._file_count += len(files)
        prefix = UNICODE_LAST_BRANCH if is_last else UNICODE_BRANCH
        self.print_files(prefix, files)
    
    def print_files(self, prefix, files):
        last = len(files) - 1
        sorted(files, key=lambda x: x.name)
        for i, x in enumerate(files):
            print prefix + self.format_leaf("{} [{:.6}]".format(x.name.encode('utf-8'), x.checksum) if x.checksum else x.name.encode('utf-8'), i == last)

    def format_leaf(self, text, is_last):
        return (UNICODE_LAST_LEAF if is_last else UNICODE_LEAF) + text
