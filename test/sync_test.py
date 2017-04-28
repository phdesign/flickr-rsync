import os, sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libs')
import mock
from modules.sync import Sync
from modules.file_info import FileInfo
from modules.folder_info import FolderInfo

class SyncTest(unittest.TestCase):

    def test_run(self):
        config = mock.MagicMock()
        src_storage = mock.MagicMock()
        src_storage.list_folders.return_value = [
            FolderInfo(id=1, name='One')
        ]
        dest_storage = mock.MagicMock()
        dest_storage.list_folders.return_value = [
            FolderInfo(id=1, name='One')
        ]

        sync = Sync(config, src_storage, dest_storage)
        sync.run()

        src_storage.list_folders.assert_called()

if __name__ == '__main__':
    unittest.main(verbosity=2)
