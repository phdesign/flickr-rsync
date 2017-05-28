from __future__ import print_function
import os
import operator
import time
from threading import current_thread
from rx import Observable, AnonymousObservable
from rx.internal import extensionmethod
from verbose import vprint
from root_folder_info import RootFolderInfo

@extensionmethod(Observable)
def when_complete(self):
    source = self

    def subscribe(observer):
        def on_completed():
            observer.on_next()
            observer.on_completed()

        return source.subscribe(on_completed=on_completed, on_error=observer.on_error)

    return AnonymousObservable(subscribe)

class Sync(object):
    
    def __init__(self, config, src, dest):
        self._config = config
        self._src = src
        self._dest = dest

    def run(self):
        if self._config.dry_run:
            print("dry run enabled, no files will be copied")
        print("building folder list...")
        start = time.time()

        dest_folders = {folder.name.lower(): folder for folder in self._dest.list_folders()}
        # Create folder stream
        src_folders = Observable.from_(self._src.list_folders()) \
            .map(lambda folder: { 'src': folder, 'dest': dest_folders.get(folder.name.lower()) }) \
            .publish().auto_connect(2)
        
        # Split into copy and merge streams
        to_copy = src_folders.filter(lambda x: x['dest'] == None)
        to_merge = src_folders.filter(lambda x: x['dest'] != None)
        if self._config.root_files:
            to_merge = to_merge.start_with({ 'src': RootFolderInfo(), 'dest': RootFolderInfo() })
        to_merge = to_merge.buffer(lambda: src_folders.when_complete()).flat_map(lambda x: x)

        # Concat streams so copy operations happen first
        pending = to_copy \
            .merge(to_merge) \
            .flat_map(lambda x: self._expand_folder(**x)) \
            .publish().auto_connect(2)
        pending \
            .subscribe(lambda x: self._copy_file(**x) if not x['exists'] else
                vprint("{}...skipped, file exists".format(x['path'])))

        # Count files, print summary
        skipped_count = pending.count(lambda x: x['exists'])
        pending \
            .count() \
            .zip(skipped_count, lambda nall, nskipped: (nall, nskipped)) \
            .subscribe(lambda (nall, nskipped), : self._print_summary(time.time() - start, nall - nskipped, nskipped))

    def _expand_folder(self, src, dest):
        is_merging = dest != None
        vprint("{} {} [{}]".format("merging" if is_merging else "copying", 
            src.name if not src.is_root else 'root', current_thread().name))
        dest_files = [f.name.lower() for f in self._dest.list_files(dest)] if is_merging else []
        source = Observable.from_(self._src.list_files(src))
        return source.map(lambda f: { 
            'folder': src,
            'file': f,
            'exists': f.name.lower() in dest_files,
            'path': os.path.join(src.name, f.name)
        })

    def _copy_file(self, folder, file, path, **kwargs):
        print(path)
        if not self._config.dry_run:
            self._src.copy_file(file, folder and folder.name, self._dest)
        vprint("{}...copied [{}]".format(path, current_thread().name))

    def _print_summary(self, elapsed, files_copied, files_skipped):
        skipped_msg = ", skipped {} files(s) that already exist".format(files_skipped) if files_skipped > 0 else ''
        print("\ntransferred {} file(s){} in {} sec".format(files_copied, skipped_msg, round(elapsed, 2)))
