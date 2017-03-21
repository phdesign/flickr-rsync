import os
import hashlib
from storage import Storage
from file_info import FileInfo
from folder_info import FolderInfo

class LocalStorage(Storage):
    
    def __init__(self, config):
        self._files_dir = config.paths['files_dir']

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
            if os.path.isdir(os.path.join(self._files_dir, x))
        ]

    def list_files(self, folder):
        folder_abs = os.path.join(self._files_dir, folder.name)
        return [
            FileInfo(id=i, name=name, checksum=self.md5_checksum(path), size=os.path.getsize(path))
            for i, (name, path) in enumerate((x, os.path.join(folder_abs, x)) for x in os.listdir(folder_abs))
            if os.path.isfile(path)
        ]
