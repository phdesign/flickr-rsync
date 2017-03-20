# -*- coding: utf-8 -*-

import operator

UNICODE_NODE = u"├───"
UNICODE_LAST_NODE = u"└───"
UNICODE_BRANCH = u"│   "
UNICODE_LAST_BRANCH = "    "

class TreeWalker(object):
    
    def __init__(self, storage):
        self._storage = storage

    def walk(self):
        folders = self._storage.list_folders()
        self.print_folders(folders)

    def print_folders(self, folders):
        last = len(folders) - 1
        for i, x in enumerate(folders):
            self.print_folder(x, i == last) 

    def print_folder(self, folder, is_last):
        print self.format_node(folder.name, is_last)

        files = self._storage.list_files(folder)
        prefix = UNICODE_LAST_BRANCH if is_last else UNICODE_BRANCH
        self.print_files(prefix, files)
    
    def print_files(self, prefix, files):
        last = len(files) - 1
        for i, x in enumerate(files):
            print prefix + self.format_node(x.name + " (" + x.checksum + ")" if x.checksum else x.name, i == last)

    def format_node(self, text, is_last):
        return (UNICODE_LAST_NODE if is_last else UNICODE_NODE) + text
