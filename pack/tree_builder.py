# -*- coding: utf-8 -*-

import operator

UNICODE_NODE = u"├───"
UNICODE_LAST_NODE = u"└───"
UNICODE_BRANCH = u"│   "
UNICODE_LAST_BRANCH = "    "

class TreeBuilder(object):
    
    def __init__(self, storage):
        self._storage = storage

    def format_tree(self):
        folders = self._storage.list_folders()
        tree = self.format_folders(folders)
        return '\n'.join(tree)

    def format_folders(self, folders):
        last = len(folders) - 1
        formatted_folders = [self.format_folder(x, i == last) for i, x in enumerate(folders)]
        return reduce(operator.concat, formatted_folders)

    def format_folder(self, folder, is_last):
        files = self._storage.list_files(folder)
        prefix = UNICODE_LAST_BRANCH if is_last else UNICODE_BRANCH
        formatted_files = [prefix + x for x in self.format_files(files)]
        return [self.format_node(folder.title, is_last)] + formatted_files
    
    def format_files(self, files):
        last = len(files) - 1
        return [self.format_node(x.title, i == last) for i, x in enumerate(files)]

    def format_node(self, text, is_last):
        return (UNICODE_LAST_NODE if is_last else UNICODE_NODE) + text
