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
        self._file_types = config.files['local_file_types']
        self._exclude = config.files['local_exclude']

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
            if (not self._exclude or not re.search(self._exclude, x, flags=re.IGNORECASE)) and
                os.path.isdir(os.path.join(self._files_dir, x))
        ]

    def list_files(self, folder):
        folder_abs = os.path.join(self._files_dir, folder.name)
        if self._file_types:
            patterns = self._file_types.split(',')
            files = itertools.chain.from_iterable(glob.glob(os.path.join(folder_abs, pattern.strip())) for pattern in patterns if pattern)
        else:
            files = (os.path.join(folder_abs, x) for x in os.listdir(folder_abs))
        return [
            FileInfo(id=i, name=name, checksum=self.md5_checksum(path), size=os.path.getsize(path))
            for i, (name, path) in enumerate((os.path.basename(x), x) for x in files)
            if (not self._exclude or not re.search(self._exclude, path, flags=re.IGNORECASE)) and
                os.path.isfile(path)
        ]
