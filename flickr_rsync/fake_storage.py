from __future__ import print_function
import os
import time
import random
from storage import Storage
from file_info import FileInfo
from folder_info import FolderInfo

class FakeStorage(Storage):
    fake_count = 0

    def __init__(self, config):
        self._config = config
        self.prefix = '' if FakeStorage.fake_count == 0 else str(FakeStorage.fake_count)
        FakeStorage.fake_count += 1

    def list_folders(self):
        folder_count = 3
        for i in range(folder_count):
            name = '{}{} Folder'.format(self.prefix, self._get_char(i, folder_count))
            yield self._intense_calculation(FolderInfo(id=i, name=name))

    def list_files(self, folder):
        if folder and folder.name == 'B Folder':
            return
        file_count = 4
        for i in range(file_count):
            name = '{}{} File'.format(self.prefix, self._get_char(i, file_count))
            yield self._intense_calculation(FileInfo(id=i, name=name))

    def copy_file(self, fileinfo, folder_name, dest_storage):
        self._intense_calculation(None)

    def _get_char(self, num, max_num):
        return str(unichr((64 + max_num) - num))

    def _intense_calculation(self, value):
        # sleep for a random short duration between 0.5 to 2.0 seconds to simulate a long-running calculation
        time.sleep(random.randint(2, 6) * .1)
        return value


