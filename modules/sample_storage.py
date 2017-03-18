from storage import Storage
from file_info import FileInfo
from folder_info import FolderInfo

class SampleStorage(Storage):
    
    def __init__(self, config):
        pass

    def list_folders(self):
        return [
            FolderInfo(id=1, name="abc", checksum=""),
            FolderInfo(id=2, name="def", checksum="")
        ]

    def list_files(self, folder):
        return [
            FileInfo(id='32876603880', name='IMG_2131', checksum=""),
            FileInfo(id='32416116504', name='IMG_2132', checksum=""),
            FileInfo(id='33218094626', name='IMG_2133', checksum=""),
            FileInfo(id='33259489725', name='IMG_2134', checksum=""),
            FileInfo(id='33218074946', name='IMG_2135', checksum=""),
            FileInfo(id='32444976173', name='IMG_2136', checksum=""),
            FileInfo(id='33131097571', name='IMG_2137', checksum=""),
            FileInfo(id='33103597842', name='IMG_2138', checksum=""),
            FileInfo(id='33131077441', name='IMG_2139', checksum="")
        ]
