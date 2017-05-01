from abc import abstractmethod

class Storage(object):

    @abstractmethod
    def list_folders(self):
        pass

    @abstractmethod
    def list_files_in_folder(self, folder):
        pass
