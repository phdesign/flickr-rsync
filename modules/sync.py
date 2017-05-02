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

        plan = self._make_plan()
        for src_folder in plan['copy']:
            print src_folder.name + os.sep
            self._copy_folder(src_folder)
        for (src_folder, dest_folder) in plan['merge']:
            print src_folder.name + os.sep
            self._merge_folders(src_folder, dest_folder)

        self._print_summary(time.time() - start)

    def _make_plan(self):
        plan = {
            'copy': [],
            'merge': []
        }
        src_folders = self._src.list_folders()
        dest_folders = self._dest.list_folders()
        for src_folder in src_folders:
            exists = False
            for dest_folder in dest_folders:
                if src_folder.name == dest_folder.name:
                    plan['merge'].append([src_folder, dest_folder])
                    exists = True
                    break
            if not exists:
                plan['copy'].append(src_folder)
        return plan

    def _copy_folder(self, folder):
        src_files = self._src.list_files(folder)
        for src_file in src_files:
            print os.path.join(folder.name, src_file.name)
            self._file_count += 1
            if not self._config.dry_run:
                self._src.copy_file(src_file, folder.name, self._dest)

    def _merge_folders(self, src_folder, dest_folder):
        src_files = self._src.list_files(src_folder)
        dest_files = self._dest.list_files(dest_folder)
        for src_file in src_files:
            exists = False
            for dest_file in dest_files:
                if src_file.name == dest_file.name:
                    exists = True
                    break
            if not exists:
                print os.path.join(src_folder.name, src_file.name)
                self._file_count += 1
                if not self._config.dry_run:
                    self._src.copy_file(src_file, src_folder.name, self._dest)
        pass

    def _print_summary(self, elapsed):
        print "\ntransferred {} file(s) in {} sec".format(self._file_count, round(elapsed, 2))
