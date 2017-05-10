from __future__ import print_function
import os
import operator
import time
from functools import partial
from rx import Observable
from rx.concurrency import ThreadPoolScheduler

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

        src_folders = Observable.from_(self._src.list_folders())
        dest_folders = {folder.name.lower(): folder for folder in self._dest.list_folders()}
        to_merge = []
        if self._config.root_files:
           src_folders = src_folders.start_with(None)
        src_folders.subscribe(
            on_next=lambda folder: to_merge.append((folder, dest_folders[folder.name.lower()])) \
                if folder.name.lower() in dest_folders else self._copy_folder(folder),
            on_completed=lambda: [self._merge_folders(src, dest) for (src, dest) in to_merge] \
                and self._print_summary(time.time() - start))

    def _copy_folder(self, folder):
        pool_scheduler = ThreadPoolScheduler(4)
        Observable.from_(self._src.list_files(folder)) \
            .observe_on(pool_scheduler) \
            .subscribe(partial(self._copy_file, folder.name))

    def _merge_folders(self, src_folder, dest_folder):
        pool_scheduler = ThreadPoolScheduler(4)
        dest_files = [fileinfo.name.lower() for fileinfo in self._dest.list_files(dest_folder)]
        Observable.from_(self._src.list_files(src_folder)) \
            .filter(lambda fileinfo: not fileinfo.name.lower() in dest_files) \
            .observe_on(pool_scheduler) \
            .subscribe(partial(self._copy_file, src_folder.name))

    def _copy_file(self, folder_name, fileinfo):
        print(os.path.join(folder_name, fileinfo.name))
        self._file_count += 1
        if not self._config.dry_run:
            self._src.copy_file(fileinfo, folder_name, self._dest)

    def _print_summary(self, elapsed):
        print("\ntransferred {} file(s) in {} sec".format(self._file_count, round(elapsed, 2)))
