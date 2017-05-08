# -*- coding: utf-8 -*-
from __future__ import print_function
import operator
import time
from walker import Walker
from rx import Observable

UNICODE_LEAF = u"├─── ".encode('utf-8')
UNICODE_LAST_LEAF = u"└─── ".encode('utf-8')
UNICODE_BRANCH = u"│   ".encode('utf-8')
UNICODE_LAST_BRANCH = "    "

def enumerate_peek(items):
    """
    Wraps an iterator or sequence of items, returning a each item and a flag indicating if there are more items to come

    Args:
        items: An iterator or sequence of items

    Returns:
        A tuple (item, has_next) where has_next indicates there are more items
    """
    iterator = iter(items)
    current = next(iterator)
    while True:
        try:
            next_item = next(iterator)
            yield (current, True)
            current = next_item
        except StopIteration:
            yield (current, False)
            return

class TreeWalker(Walker):
    
    def __init__(self, config, storage):
        self._config = config
        self._storage = storage
        self._file_count = 0
        self._hidden_folder_count = 0
        self._folder_count = 0

    def walk(self):
        start = time.time()

        folders = Observable.from_(self._storage.list_folders())
        if self._config.root_files:
           folders = folders.start_with(None) 
        files = folders.concat_map(lambda folder: Observable.from_((fileinfo, folder) for fileinfo in self._storage.list_files(folder)))
        if self._config.list_sort:
            files.to_sorted_list(key_selector=lambda (fileinfo, folder): (folder.name if folder else '', fileinfo.name)) \
                .subscribe(on_next=lambda items: [self._print_file(folder, fileinfo) for fileinfo, folder in items],
                    on_completed=lambda: self._print_summary(time.time() - start))
        else:
            files.subscribe(on_next=lambda (fileinfo, folder): self._print_file(folder, fileinfo),
                on_completed=lambda: self._print_summary(time.time() - start))

    def _print_file(self, folder, fileinfo):
        print("{}{}{}".format(UNICODE_LEAF, fileinfo.name, fileinfo.checksum or ''))

    def _walk(self):
        start = time.time()
        folders = self._storage.list_folders()
        if self._config.list_sort:
            folders = sorted(folders, key=lambda x: x.name)
        if self._config.root_files:
            self._print_root_files(any(folders))
        self._print_folders(folders)

        self._print_summary(time.time() - start)

    def _print_root_files(self, has_folders):
        files = self._storage.list_files(None)
        if self._config.list_sort:
            files = sorted(files, key=lambda x: x.name)
        for x, has_next in enumerate_peek(files):
            self._file_count += 1
            print(self._format_leaf(
                "{} [{:.6}]".format(x.name.encode('utf-8'), x.checksum) if x.checksum else x.name.encode('utf-8'), 
                not has_next and not has_folders))

    def _print_folders(self, folders):
        is_first = True
        for x, has_next in enumerate_peek(folders):
            self._print_folder(x, is_first, not has_next) 
            is_first = False

    def _print_folder(self, folder, is_first, is_last):
        files = self._storage.list_files(folder)
        if self._config.list_sort:
            files = sorted(files, key=lambda x: x.name)
        if not any(files):
            self._hidden_folder_count += 1
            return
        if is_first and self._file_count > 0:
            print(UNICODE_BRANCH)
        print(self._format_leaf(folder.name.encode('utf-8'), is_last))
        self._folder_count += 1
        prefix = UNICODE_LAST_BRANCH if is_last else UNICODE_BRANCH
        self._print_files(prefix, files)
        if not is_last:
            print(UNICODE_BRANCH)
    
    def _print_files(self, prefix, files):
        for x, has_next in enumerate_peek(files):
            self._file_count += 1
            print(prefix + self._format_leaf(
                "{} [{:.6}]".format(x.name.encode('utf-8'), x.checksum) if x.checksum else x.name.encode('utf-8'), 
                not has_next))

    def _format_leaf(self, text, is_last):
        return (UNICODE_LAST_LEAF if is_last else UNICODE_LEAF) + text

    def _print_summary(self, elapsed):
        print("{} directories, {} files{} read in {} sec".format(self._folder_count, self._file_count,
            " (excluding {} empty directories)".format(self._hidden_folder_count) if self._hidden_folder_count > 0 else "",
            round(elapsed, 2)))
