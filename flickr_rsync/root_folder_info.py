from folder_info import FolderInfo

class RootFolderInfo(FolderInfo):

    def __init__(self):
        super(RootFolderInfo, self).__init__(id=None, name='', full_path=None)
        self.is_root = True

