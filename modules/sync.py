from __future__ import print_function
import os
import operator
import time
from rx import Observable
from rx.core import Scheduler
from threading import current_thread
from functools import partial
from rx.concurrency import ThreadPoolScheduler

class Sync(object):
    
    def __init__(self, config, src, dest):
        self._config = config
        self._src = src
        self._dest = dest
        self._file_count = 0
        self._pool_scheduler = ThreadPoolScheduler(4)

    def run(self):
        if self._config.dry_run:
            print("dry run enabled, no files will be copied")
        print("building folder list...")
        self.run_start()

    def run_subscribe(self):
        start = time.time()

        def done():
            for (src, dest) in to_merge:
                self._merge_folders(src, dest)
            print("done. thread: " + current_thread().name)

        src_folders = Observable.from_(self._src.list_folders())
        dest_folders = {folder.name.lower(): folder for folder in self._dest.list_folders()}
        to_merge = []
        if self._config.root_files:
           src_folders = src_folders.start_with(None)
        src_folders.subscribe(
            on_next=lambda folder: to_merge.append((folder, dest_folders[folder.name.lower()])) \
                if folder.name.lower() in dest_folders else self._copy_folder(folder),
            on_completed=done)
        self._print_summary(time.time() - start)

    def run_start(self):
        start = time.time()

        def _copy_folder(folder):
            print("copy " + folder.name + " thread: " + current_thread().name)
            return Observable.from_(self._src.list_files(folder)) \
                .flat_map(lambda f: Observable.start(lambda: self._copy_file(folder.name, f)))

        def _merge_folders(src_folder, dest_folder):
            print("merge " + folder.name + " thread: " + current_thread().name)
            dest_files = [fileinfo.name.lower() for fileinfo in self._dest.list_files(dest_folder)]
            return Observable.from_(self._src.list_files(src_folder)) \
                .filter(lambda fileinfo: not fileinfo.name.lower() in dest_files) \
                .flat_map(lambda f: Observable.start(lambda: self._copy_file(folder.name, f)))

        src_folders = Observable.from_(self._src.list_folders())
        dest_folders = {folder.name.lower(): folder for folder in self._dest.list_folders()}
        to_merge = []
        if self._config.root_files:
           src_folders = src_folders.start_with(None)
        src_folders \
            .flat_map(lambda f: _merge_folders(f, dest_folders[f.name.lower()]) \
                if f.name.lower() in dest_folders else _copy_folder(f)) \
            .observe_on(Scheduler.event_loop) \
            .to_blocking() \
            .subscribe(
                on_next=lambda x: print("on_next: {}, thread: {}".format(x, current_thread().name)),
                on_completed=lambda: print("done. thread: " + current_thread().name),
                on_error=lambda err: print("err: {}".format(err)))
        
        self._print_summary(time.time() - start)
        time.sleep(2)

    def run_observe_on(self):
        start = time.time()

        def _copy_folder(folder):
            print("copy " + folder.name + " thread: " + current_thread().name)
            return Observable.from_(self._src.list_files(folder)) \
                .observe_on(self._pool_scheduler) \
                .flat_map(partial(self._copy_file, folder.name))

        def _merge_folders(src_folder, dest_folder):
            print("merge " + folder.name + " thread: " + current_thread().name)
            dest_files = [fileinfo.name.lower() for fileinfo in self._dest.list_files(dest_folder)]
            return Observable.from_(self._src.list_files(src_folder)) \
                .filter(lambda fileinfo: not fileinfo.name.lower() in dest_files) \
                .observe_on(self._pool_scheduler) \
                .flat_map(partial(self._copy_file, folder.name))

        src_folders = Observable.from_(self._src.list_folders())
        dest_folders = {folder.name.lower(): folder for folder in self._dest.list_folders()}
        to_merge = []
        if self._config.root_files:
           src_folders = src_folders.start_with(None)
        src_folders \
            .flat_map(lambda f: _merge_folders(f, dest_folders[f.name.lower()]) \
                if f.name.lower() in dest_folders else _copy_folder(f)) \
            .observe_on(Scheduler.event_loop) \
            .subscribe(on_completed=lambda: print("done. thread: " + current_thread().name))
        
        self._print_summary(time.time() - start)

    def _copy_folder(self, folder):
        print("copy " + folder.name + " thread: " + current_thread().name)
        source = Observable.from_(self._src.list_files(folder)) \
            .observe_on(self._pool_scheduler)
        source.to_blocking().subscribe(partial(self._copy_file, folder.name))
        return source

    def _merge_folders(self, src_folder, dest_folder):
        print("merge " + folder.name + " thread: " + current_thread().name)
        dest_files = [fileinfo.name.lower() for fileinfo in self._dest.list_files(dest_folder)]
        source = Observable.from_(self._src.list_files(src_folder)) \
            .filter(lambda fileinfo: not fileinfo.name.lower() in dest_files) \
            .observe_on(self._pool_scheduler)
        source.to_blocking().subscribe(partial(self._copy_file, src_folder.name))
        return source

    def _copy_file(self, folder_name, fileinfo):
        print(os.path.join(folder_name, fileinfo.name) + " thread: " + current_thread().name)
        self._file_count += 1
        if not self._config.dry_run:
            self._src.copy_file(fileinfo, folder_name, self._dest)

    def _print_summary(self, elapsed):
        print("\ntransferred {} file(s) in {} sec".format(self._file_count, round(elapsed, 2)) + " thread: " + current_thread().name)
