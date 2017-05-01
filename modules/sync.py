import os
import operator
import time

class Sync(object):
    
    def __init__(self, config, src, dest):
        self._config = config
        self._src = src
        self._dest = dest
        self._file_count = 0

    def run(self):
        if self._config.dry_run:
            print "dry run enabled, simulating operation only...\n"
        start = time.time()
        self._src_folders = self._src.list_folders()
        self._dest_folders = self._dest.list_folders()
        self._copy_shallow()
        self._print_summary(time.time() - start)

    def _copy_shallow(self):
        for src_folder in self._src_folders:
            print src_folder.name + os.sep
            exists = False
            for dest_folder in self._dest_folders:
                if src_folder.name == dest_folder.name:
                    exists = True
                    break
            if not exists:
                self._copy_folder(src_folder)

    def _copy_deep(self):
        pass

    def _copy_folder(self, folder):
        files = self._src.list_files_in_folder(folder)
        for file_to_copy in files:
            print os.path.join(folder.name, file_to_copy.name)
            self._file_count += 1
            if not self._config.dry_run:
                self._src.copy_file(file_to_copy, folder.name, self._dest)

    def _print_summary(self, elapsed):
        print "\ntransferred {} file(s) in {} sec".format(self._file_count, round(elapsed, 2))
