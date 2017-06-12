# -*- coding: utf-8 -*-
from __future__ import print_function
import operator
import time
from rx import Observable, AnonymousObservable
from rx.internal import extensionmethod
from walker import Walker
from root_folder_info import RootFolderInfo

UNICODE_LEAF = u"├─── ".encode('utf-8')
UNICODE_LAST_LEAF = u"└─── ".encode('utf-8')
UNICODE_BRANCH = u"│   ".encode('utf-8')
UNICODE_LAST_BRANCH = "    "

@extensionmethod(Observable)
def is_last(source):
    def subscribe(observer):
        value = [None]
        seen_value = [False]

        def on_next(x):
            if seen_value[0]:
                observer.on_next((value[0], False))
            value[0] = x
            seen_value[0] = True

        def on_completed():
            if seen_value[0]:
                observer.on_next((value[0], True))
            observer.on_completed()

        return source.subscribe(on_next, observer.on_error, on_completed)
    return AnonymousObservable(subscribe)

class TreeWalker(Walker):
    
    def __init__(self, config, storage):
        self._config = config
        self._storage = storage

    def walk(self):
        start = time.time()

        # Create source stream with folder message items
        folderlist = self._storage.list_folders()
        if self._config.list_sort:
            folderlist = sorted(folderlist, key=lambda x: x.name)
        folders = Observable.from_(folderlist) \
            .map(lambda f: { 'folder': f })
        if self._config.root_files:
            folders = folders.start_with({ 'folder': RootFolderInfo() }) 

        # Expand folder messages into file messages
        folders = folders.publish().auto_connect(2)
        files = folders.is_last() \
            .map(lambda (x, is_last): dict(x, is_last_folder=is_last))
        if not self._config.list_folders:
            files = files.concat_map(lambda x: self._walk_folder(x))
        # Group by folder but still provide a file stream within each group
        groups = files.group_by(lambda x: x['folder'])
        groups.subscribe(self._walk_group)

        # Gather counts and print summary
        all_folder_count = folders.count(self._not_root)
        shown_folder_count = groups \
            .flat_map(lambda g: g.first()) \
            .count(self._not_root)
        files.count() \
            .zip(shown_folder_count, all_folder_count, lambda n_files, n_shown, n_all: (n_files, n_shown, n_all - n_shown)) \
            .subscribe(lambda (n_files, n_shown, n_hidden): self._print_summary(time.time() - start, n_files, n_shown, n_hidden))

    def _not_root(self, x):
        return not x['folder'].is_root

    def _walk_group(self, source):
        seen_value = [False]

        def on_next(x):
            if not seen_value[0] and self._not_root(x):
                self._print_folder(**x)
            if 'file' in x:
                self._print_file(**dict(x, is_root_folder=x['folder'].is_root))
            seen_value[0] = True

        source.subscribe(on_next)

    def _walk_folder(self, msg):
        fileList = self._storage.list_files(msg['folder'])
        if self._config.list_sort:
            fileList = sorted(fileList, key=lambda x: x.name)

        return Observable.from_(fileList).is_last() \
            .map(lambda (f, is_last): dict(msg, file=f, is_last_file=is_last))

    def _print_folder(self, folder, is_last_folder, **kwargs):
        print("{}{}".format(UNICODE_LAST_LEAF if is_last_folder else UNICODE_LEAF, folder.name))

    def _print_file(self, file, is_last_file, is_last_folder, is_root_folder, **kwargs):
        folder_prefix = ''
        if not is_root_folder:
            if is_last_folder:
                folder_prefix = UNICODE_LAST_BRANCH
            else:
                folder_prefix = UNICODE_BRANCH
        file_prefix = UNICODE_LEAF
        if is_last_file and (not is_root_folder or is_last_folder):
            file_prefix = UNICODE_LAST_LEAF

        print("{}{}{}{}".format(folder_prefix, file_prefix, file.name,
            " [{:.6}]".format(file.checksum) if file.checksum else ''))
        if is_last_file and not is_last_folder:
            print(UNICODE_BRANCH)

    def _print_summary(self, elapsed, file_count, folder_count, hidden_folder_count):
        print("{} directories{}{} read in {} sec".format(folder_count, 
            ", {} files".format(file_count) if not self._config.list_folders else "",
            " (excluding {} empty directories)".format(hidden_folder_count) if hidden_folder_count > 0 else "",
            round(elapsed, 2)))
