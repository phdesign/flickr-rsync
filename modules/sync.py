from __future__ import print_function
import os
import operator
import time
from rx import Observable

class Sync(object):
    
    def __init__(self, config, src, dest):
        self._config = config
        self._src = src
        self._dest = dest
        self._file_count = 0

    def run(self):
        if self._config.dry_run:
            print("dry run enabled, no files will be copied")
        print("building folder list...")
        start = time.time()

        dest_folders = {folder.name.lower(): folder for folder in self._dest.list_folders()}
        src_folders = Observable.from_(self._src.list_folders())
        to_merge = []
        if self._config.root_files:
           src_folders = src_folders.start_with(None)
        src_folders.subscribe(
            on_next=lambda folder: to_merge.append((folder, dest_folders[folder.name.lower()])) \
                if folder.name.lower() in dest_folders else self._copy_folder(folder),
            on_completed=lambda: [self._merge_folders(src, dest) for (src, dest) in to_merge] \
                and self._print_summary(time.time() - start))

    def _copy_folder(self, folder):
        src_files = self._src.list_files(folder)
        for src_file in src_files:
            print(os.path.join(folder.name, src_file.name))
            self._file_count += 1
            if not self._config.dry_run:
                self._src.copy_file(src_file, folder.name, self._dest)

    def _merge_folders(self, src_folder, dest_folder):
        src_files = self._src.list_files(src_folder)
        dest_files = self._dest.list_files(dest_folder)
        for src_file in src_files:
            file_exists = next((True for x in dest_files if x.name.lower() == src_file.name.lower()), False)
            if not file_exists:
                print(os.path.join(src_folder.name, src_file.name))
                self._file_count += 1
                if not self._config.dry_run:
                    self._src.copy_file(src_file, src_folder.name, self._dest)
        pass

    def _print_summary(self, elapsed):
        print("\ntransferred {} file(s) in {} sec".format(self._file_count, round(elapsed, 2)))
