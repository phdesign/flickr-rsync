import os
import re
import glob
import itertools
import hashlib
from storage import Storage
from file_info import FileInfo
from folder_info import FolderInfo

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
        return [
            FolderInfo(id=i, name=x)
            for i, x in enumerate(os.listdir(self.path))
            if (not self._config.include_dir or re.search(self._config.include_dir, x, flags=re.IGNORECASE)) and
                (not self._config.exclude_dir or not re.search(self._config.exclude_dir, x, flags=re.IGNORECASE)) and
                os.path.isdir(os.path.join(self.path, x))
        ]

    def list_files(self, folder):
        folder_abs = os.path.join(self.path, folder.name) if folder else self.path
        return [
            FileInfo(id=i, name=name, checksum=self.md5_checksum(path))
            for i, (name, path) in enumerate((x, os.path.join(folder_abs, x)) for x in os.listdir(folder_abs))
            if (not self._config.include or re.search(self._config.include, path, flags=re.IGNORECASE)) and
                (not self._config.exclude or not re.search(self._config.exclude, path, flags=re.IGNORECASE)) and
                os.path.isfile(path)
        ]
