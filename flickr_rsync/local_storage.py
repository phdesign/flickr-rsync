from __future__ import print_function
import os
import re
import glob
import itertools
import hashlib
import shutil
from storage import Storage, RemoteStorage
from file_info import FileInfo
from folder_info import FolderInfo
from verbose import vprint

def mkdirp(path):
    """
    Creates all missing folders in the path

    Args:
        path: A file system path to create, may include a filename (ignored)
    """
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as ex: # Guard against race condition
            if ex.errno != errno.EEXIST:
                raise

class LocalStorage(Storage):
    
    def __init__(self, config, path):
        self.path = path
        self._config = config

    def md5_checksum(self, file_path):
        with open(file_path, 'rb') as fh:
            m = hashlib.md5()
            while True:
                data = fh.read(8192)
                if not data:
                    break
                m.update(data)
            return m.hexdigest()

    def list_folders(self):
        vprint("using base folder {}".format(self.path))
        return [
            FolderInfo(id=i, name=name.encode('utf-8'), full_path=path.encode('utf-8'))
            for i, (name, path) in enumerate((x, os.path.join(self.path, x)) for x in os.listdir(self.path))
            if self._should_include(name, self._config.include_dir, self._config.exclude_dir) and os.path.isdir(path)
        ]

    def list_files(self, folder):
        folder_abs = os.path.join(self.path, folder.name)
        return [
            FileInfo(
                id=i, 
                name=name.encode('utf-8'), 
                full_path=path.encode('utf-8'), 
                checksum=self.md5_checksum(path) if self._config.checksum else None)
            for i, (name, path) in enumerate((x, os.path.join(folder_abs, x)) for x in os.listdir(folder_abs))
            if self._should_include(path, self._config.include, self._config.exclude) and os.path.isfile(path)
        ]

    def copy_file(self, file_info, folder_name, dest_storage):
        src = file_info.full_path
        if isinstance(dest_storage, RemoteStorage):
            dest_storage.upload(src, folder_name, file_info.name, file_info.checksum)
        else:
            relative_path = os.path.join(folder_name, file_info.name)
            dest = os.path.join(dest_storage.path, relative_path)
            mkdirp(dest)
            shutil.copyfile(src, dest)

    def _should_include(self, name, include_pattern, exclude_pattern):
        return ((not include_pattern or re.search(include_pattern, name, flags=re.IGNORECASE)) and
            (not exclude_pattern or not re.search(exclude_pattern, name, flags=re.IGNORECASE)))
