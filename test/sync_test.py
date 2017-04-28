import os, sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libs')
from mock import MagicMock
from modules.sync import Sync
from modules.file_info import FileInfo
from modules.folder_info import FolderInfo

class SyncTest(unittest.TestCase):

    def run_should_call_copy_folder_for_each_missing_folder_in_src(self):
        config = MagicMock()
        src_storage = MagicMock()
        folder_one = FolderInfo(id=1, name='One')
        src_storage.list_folders.return_value = [folder_one]
        dest_storage = MagicMock()
        dest_storage.list_folders.return_value = []

        sync = Sync(config, src_storage, dest_storage)
        sync._copy_folder = MagicMock()
        sync.run()

        sync._copy_folder.assert_called_once_with(folder_one)

if __name__ == '__main__':
    unittest.main(verbosity=2)
