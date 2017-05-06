from __future__ import print_function
import time
import random
from storage import Storage
from file_info import FileInfo
from folder_info import FolderInfo

class FakeStorage(Storage):

    def __init__(self, config):
        self._config = config

    def list_folders(self):
        for i in range(5):
            yield self._intense_calculation(FolderInfo(id=i, name="{} Folder".format(i)))

    def list_files(self, folder):
        for i in range(5):
            yield self._intense_calculation(FileInfo(id=i, name="{} File".format(i)))

    def _intense_calculation(self, value):
        # sleep for a random short duration between 0.5 to 2.0 seconds to simulate a long-running calculation
        time.sleep(random.randint(5, 10) * .1)
        return value


