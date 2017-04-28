import operator
from walker import Walker

class CsvWalker(Walker):
    
    def __init__(self, config, storage):
        self._config = config
        self._storage = storage

    def walk(self):
        folders = self._storage.list_folders()
        print "Folder, Filename, Checksum"
        if self._config.root_files:
            self._print_root_files()
        self._print_folders(folders)

    def _print_root_files(self):
        files = self._storage.list_files(None)
        if len(files) == 0:
            return;
        self._print_files("", files)

    def _print_folders(self, folders):
        last = len(folders) - 1
        sorted(folders, key=lambda x: x.name)
        for i, x in enumerate(folders):
            self._print_folder(x, i == last) 

    def _print_folder(self, folder, is_last):
        files = self._storage.list_files(folder)
        if len(files) == 0:
            return
        self._print_files(folder.name.encode('utf-8'), files)
    
    def _print_files(self, folder_name, files):
        sorted(files, key=lambda x: x.name)
        for i, x in enumerate(files):
            print "{}, {}, {}".format(folder_name, x.name.encode('utf-8'), x.checksum)

