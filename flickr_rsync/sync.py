from __future__ import print_function
import os
import operator
import time
from verbose import vprint
from root_folder_info import RootFolderInfo

class Sync(object):
    
    def __init__(self, config, src, dest):
        self._config = config
        self._src = src
        self._dest = dest
        self._copy_count = 0
        self._skip_count = 0

    def run(self):
        if self._config.dry_run:
            print("dry run enabled, no files will be copied")
        print("building folder list...")
        start = time.time()

        src_folders = self._src.list_folders()
        dest_folders = {folder.name.lower(): folder for folder in self._dest.list_folders()}
        for src_folder in src_folders:
            dest_folder = dest_folders.get(src_folder.name.lower())
            if dest_folder:
                print(src_folder.name + os.sep)
                self._merge_folders(src_folder, dest_folder)
            else:
                print(src_folder.name + os.sep)
                self._copy_folder(src_folder)
        # Merge root files if requested
        if self._config.root_files:
            self._merge_folders(RootFolderInfo(), RootFolderInfo())

        self._print_summary(time.time() - start, self._copy_count, self._skip_count)

    def _copy_folder(self, folder):
        src_files = self._src.list_files(folder)
        for src_file in src_files:
            path = os.path.join(folder.name, src_file.name)
            self._copy_count += 1
            self._copy_file(folder, src_file, path)

    def _merge_folders(self, src_folder, dest_folder):
        src_files = self._src.list_files(src_folder)
        dest_files = [file.name.lower() for file in self._dest.list_files(dest_folder)]
        for src_file in src_files:
            path = os.path.join(src_folder.name, src_file.name)
            lower_filename = src_file.name.lower()
            file_exists = lower_filename in dest_files
            # Fix for flickr converting .jpeg to .jpg.
            if lower_filename.endswith(".jpeg"):
                file_exists = file_exists or "{}.jpg".format(lower_filename[:-5]) in dest_files
            if not file_exists:
                self._copy_count += 1
                self._copy_file(src_folder, src_file, path)
            else:
                self._skip_count += 1
                vprint("{}...skipped, file exists".format(path))
        pass

    def _copy_file(self, folder, file, path):
        print(path)
        if not self._config.dry_run:
            self._src.copy_file(file, folder and folder.name, self._dest)
        vprint("{}...copied".format(path))

    def _print_summary(self, elapsed, files_copied, files_skipped):
        skipped_msg = ", skipped {} files(s) that already exist".format(files_skipped) if files_skipped > 0 else ''
        print("\ntransferred {} file(s){} in {} sec".format(files_copied, skipped_msg, round(elapsed, 2)))

