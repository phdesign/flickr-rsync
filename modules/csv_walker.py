from __future__ import print_function
from walker import Walker
from rx import Observable

class CsvWalker(Walker):
    
    def __init__(self, config, storage):
        self._config = config
        self._storage = storage

    def walk(self):
        print("Folder, Filename, Checksum")

        source = Observable.from_(self._storage.list_folders()) \
            .flat_map(lambda folder: ((fileinfo, folder) for fileinfo in self._storage.list_files(folder)))
        if self._config.root_files:
           source.start_with(self._storage.list_files(None)) 
        if self._config.list_sort:
            source.to_sorted_list(key_selector=lambda (fileinfo, folder): (folder.name, fileinfo.name)) \
                .subscribe(lambda items: [self._print_file(folder, fileinfo) for fileinfo, folder in items])
        else:
            source.subscribe(lambda (fileinfo, folder): self._print_file(folder, fileinfo))
    
    def _print_file(self, folder, fileinfo):
        print("{}, {}, {}".format(folder.name, fileinfo.name.encode('utf-8'), fileinfo.checksum))


