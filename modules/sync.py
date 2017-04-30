# -*- coding: utf-8 -*-

import operator

class Sync(object):
    
    def __init__(self, config, src, dest):
        self._config = config
        self._src = src
        self._dest = dest

    def run(self):
        self._src_folders = self._src.list_folders()
        self._dest_folders = self._dest.list_folders()
        self._copy_shallow()

    def _copy_shallow(self):
        for src_folder in self._src_folders:
            exists = False
            for dest_folder in self._dest_folders:
                if src_folder.name == dest_folder.name:
                    exists = True
                    break
            if not exists:
                self._copy_folder(src_folder)

    def _copy_deep(self):
        pass

    def _copy_folder(self, folder):
        print "Copying folder " + folder.name
        files = self._src.list_files_in_folder(folder)
        for file_to_copy in files:
            self._src.copy_file(file_to_copy, folder.name, self._dest)
