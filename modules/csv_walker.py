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

        folders = Observable.from_(self._storage.list_folders()) \
            .flat_map(lambda folder: ((fileinfo, folder) for fileinfo in self._storage.list_files(folder)))
        if self._config.list_sort:
            folders.to_sorted_list(key_selector=lambda (fileinfo, folder): '{}x{}'.format(folder.name, fileinfo.name)) \
                .subscribe(lambda items: [self._print_file(folder, fileinfo) for fileinfo, folder in items])
        else:
            folders.subscribe(lambda (fileinfo, folder): self._print_file(folder, fileinfo))
    
    def _print_file(self, folder, fileinfo):
        print("{}, {}, {}".format(folder.name, fileinfo.name.encode('utf-8'), fileinfo.checksum))


