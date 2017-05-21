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

        folderlist = self._storage.list_folders()
        if self._config.list_sort:
            folderlist = sorted(folderlist, key=lambda x: x.name)
        folders = Observable.from_(folderlist)
        if self._config.root_files:
           folders = folders.start_with(None) 

        folders = folders.publish().auto_connect(3)
        folders.count().subscribe(lambda n: print("folders: {}".format(n)))
        last = folders \
            .last() \
            .map(lambda f: (f, True))
        source = folders \
            .pairwise() \
            .map(lambda (f, b): (f, False)) \
            .merge(last) \
            .concat_map(lambda (f, is_last): self._walk_folder(f, is_last)) \
            .publish() \
            .auto_connect(2)
        source \
            .filter(lambda x: 'file' in x) \
            .subscribe(lambda x: self._print_file(x['file'], x['is_last_file'], x['is_last_folder'], x['is_root_folder']))
        source \
            .filter(lambda x: 'folder' in x and x['folder']) \
            .subscribe(lambda x: self._print_folder(x['folder'], x['is_last_folder']))
            # .count() \
            # .subscribe(lambda n: print("files: {}".format(n)))
            # .ignore_elements() \
            # .subscribe(on_completed=lambda: self._print_summary(time.time() - start))

    def _walk_folder(self, folder, is_last):
        fileList = self._storage.list_files(folder)
        if self._config.list_sort:
            fileList = sorted(fileList, key=lambda x: x.name)

        files = Observable.from_(fileList).publish().auto_connect(2)
        last = files \
            .last() \
            .map(lambda f: { 
                'file': f,
                'is_last_file': True,
                'is_last_folder': is_last,
                'is_root_folder': folder == None
            })
        files = files \
            .pairwise() \
            .map(lambda (f, b): { 
                'file': f,
                'is_last_file': False,
                'is_last_folder': is_last,
                'is_root_folder': folder == None
            }) \
            .merge(last)

        return Observable.just(folder) \
            .map(lambda f: { 
                'folder': f,
                'is_last_folder': is_last
            }) \
            .merge(files)

    def _print_folder(self, folder, is_last):
        print("{}{}".format(UNICODE_LAST_LEAF if is_last else UNICODE_LEAF, folder.name))

    def _print_file(self, fileinfo, is_last_file, is_last_folder, is_root_folder):
        folder_prefix = ''
        if not is_root_folder:
            if is_last_folder:
                folder_prefix = UNICODE_LAST_BRANCH
            else:
                folder_prefix = UNICODE_BRANCH
        file_prefix = UNICODE_LEAF
        if is_last_file and (not is_root_folder or is_last_folder):
            file_prefix = UNICODE_LAST_LEAF

        print("{}{}{}{}".format(folder_prefix, file_prefix, fileinfo.name,
            " [{:.6}]".format(fileinfo.checksum) if fileinfo.checksum else ''))
        if is_last_file and not is_last_folder:
            print(UNICODE_BRANCH)

    '''
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
    '''

    def _print_summary(self, elapsed):
        print("{} directories, {} files{} read in {} sec".format(self._folder_count, self._file_count,
            " (excluding {} empty directories)".format(self._hidden_folder_count) if self._hidden_folder_count > 0 else "",
            round(elapsed, 2)))
