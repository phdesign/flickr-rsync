# -*- coding: utf-8 -*-

import operator

class Sync(object):
    
    def __init__(self):
        pass

    def run(self, from_storage, to_storage):
        self._from_storage = from_storage
        self._to_storage = to_storage
        self._from_folders = sorted(from_storage.list_folders(), key=lambda x: x.name)
        self._to_folders = sorted(to_storage.list_folders(), key=lambda x: x.name)

    def _shallow(self):
        for from_folder in self._from_folders:
            exists = False
            for to_folder in self._to_folders:
                if from_folder.name == to_folder.name:
                    exists = True
                    break
                if from_folder.name > to_folder.name:
                    break
            if not exists:
                self._copy_folder(from_folder)

    def _deep(self):
        pass

    def _copy_folder(self, folder):
        print "Copying folder " + folder.name
