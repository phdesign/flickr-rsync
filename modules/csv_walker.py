from __future__ import print_function
import operator
from walker import Walker
from rx import Observable

class CsvWalker(Walker):
    
    def __init__(self, config, storage):
        self._config = config
        self._storage = storage

    def walk(self):
        print("Folder, Filename, Checksum")

        # folders = Observable.from_(self._storage.list_folders()).publish().auto_connect(2)
        # root_files = Observable.from_((x, None) for x in self._storage.list_files(None))
        # folders.subscribe(lambda folder: print("{}".format(folder.name)))
        # folders.flat_map(lambda folder: ((x, folder) for x in self._storage.list_files(folder))) \
            # .start_with(root_files) \
            # .subscribe(lambda (x, folder): print("{}, {}, {}".format(folder.name, x.name.encode('utf-8'), x.checksum)))

        Observable.from_(self._storage.list_folders()) \
            .flat_map(lambda folder: ((x, folder) for x in self._storage.list_files(folder))) \
            .subscribe(lambda (x, folder): print("{}, {}, {}".format(folder.name, x.name.encode('utf-8'), x.checksum)))

        # if self._config.list_sort:
            # folders = sorted(folders, key=lambda x: x.name)
        # print("Folder, Filename, Checksum")
        # if self._config.root_files:
            # self._print_root_files()
        # self._print_folders(folders)

    def _print_root_files(self):
        files = self._storage.list_files(None)
        if self._config.list_sort:
            files = sorted(files, key=lambda x: x.name)
        self._print_files("", files)

    def _print_folders(self, folders):
        for x in folders:
            self._print_folder(x) 

    def _print_folder(self, folder):
        files = self._storage.list_files(folder)
        if self._config.list_sort:
            files = sorted(files, key=lambda x: x.name)
        self._print_files(folder.name.encode('utf-8'), files)
    
    def _print_files(self, folder_name, files):
        for i, x in enumerate(files):
            print("{}, {}, {}".format(folder_name, x.name.encode('utf-8'), x.checksum))

