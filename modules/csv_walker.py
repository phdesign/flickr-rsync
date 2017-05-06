from __future__ import print_function
from walker import Walker
from rx import Observable

class CsvWalker(Walker):
    
    def __init__(self, config, storage):
        self._config = config
        self._storage = storage

    def walk(self):
        print("Folder, Filename, Checksum")

        folders = Observable.from_(self._storage.list_folders())
        if self._config.root_files:
           folders = folders.start_with(None) 
        files = folders.flat_map(lambda folder: ((fileinfo, folder) for fileinfo in self._storage.list_files(folder)))
        if self._config.list_sort:
            files.to_sorted_list(key_selector=lambda (fileinfo, folder): (folder.name if folder else '', fileinfo.name)) \
                .subscribe(lambda items: [self._print_file(folder, fileinfo) for fileinfo, folder in items])
        else:
            files.subscribe(lambda (fileinfo, folder): self._print_file(folder, fileinfo))
    
    def _print_file(self, folder, fileinfo):
        print("{}, {}, {}".format(folder.name if folder else '', fileinfo.name.encode('utf-8'), fileinfo.checksum))


