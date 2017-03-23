import os
import re
import glob
import itertools
import hashlib
from storage import Storage
from file_info import FileInfo
from folder_info import FolderInfo

class LocalStorage(Storage):
    
    def __init__(self, config):
        self._files_dir = config.files['files_dir']
        self._include = config.files['local_include']
        self._include_dir = config.files['local_include_dir']
        self._exclude = config.files['local_exclude']
        self._exclude_dir = config.files['local_exclude_dir']

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
        return [
            FolderInfo(id=i, name=x)
            for i, x in enumerate(os.listdir(self._files_dir))
            if (not self._include_dir or re.search(self._include_dir, x, flags=re.IGNORECASE)) and
                (not self._exclude_dir or not re.search(self._exclude_dir, x, flags=re.IGNORECASE)) and
                os.path.isdir(os.path.join(self._files_dir, x))
        ]

    def list_files(self, folder):
        folder_abs = os.path.join(self._files_dir, folder.name)
        return [
            FileInfo(id=i, name=name, checksum=self.md5_checksum(path))
            for i, (name, path) in enumerate((x, os.path.join(folder_abs, x)) for x in os.listdir(folder_abs))
            if (not self._include or re.search(self._include, path, flags=re.IGNORECASE)) and
                (not self._exclude or not re.search(self._exclude, path, flags=re.IGNORECASE)) and
                os.path.isfile(path)
        ]
