# -*- coding: utf-8 -*-

import operator

UNICODE_LEAF = u"├─── "
UNICODE_LAST_LEAF = u"└─── "
UNICODE_BRANCH = u"│   "
UNICODE_LAST_BRANCH = "    "

class TreeWalker(object):
    
    def __init__(self, storage):
        self._storage = storage
        self._file_count = 0

    def walk(self):
        folders = self._storage.list_folders()
        self.print_folders(folders)
        print "%i directories, %i files" % (len(folders), self._file_count)

    def print_folders(self, folders):
        last = len(folders) - 1
        for i, x in enumerate(folders):
            self.print_folder(x, i == last) 

    def print_folder(self, folder, is_last):
        print self.format_leaf(folder.name, is_last)

        files = self._storage.list_files(folder)
        self._file_count += len(files)
        prefix = UNICODE_LAST_BRANCH if is_last else UNICODE_BRANCH
        self.print_files(prefix, files)
    
    def print_files(self, prefix, files):
        formatted_files = [{
            'name': x.name, 
            'filesize': "{:.0f}kb".format(x.size / 1024.0) if x.size else "", 
            'checksum': x.checksum if x.checksum else ""
        } for x in files]
        last = len(formatted_files) - 1
        filesize_colwidth = max(len(x['filesize']) for x in formatted_files)
        for i, x in enumerate(formatted_files):
            name = x['name']
            filesize = "{:>{}}".format(x['filesize'], filesize_colwidth)
            checksum = "{:.6}".format(x['checksum'])
            meta = [x for x in [filesize, checksum] if x is not None]
            if len(meta) > 0:
                name = "[%s] " % " ".join(meta) + name
            print prefix + self.format_leaf(name, i == last)

    def format_leaf(self, text, is_last):
        return (UNICODE_LAST_LEAF if is_last else UNICODE_LEAF) + text
