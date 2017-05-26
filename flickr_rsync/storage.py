from abc import abstractmethod

class Storage(object):

    @abstractmethod
    def list_folders(self):
        pass

    @abstractmethod
    def list_files(self, folder):
        pass

    @abstractmethod
    def copy_file(self, file_info, folder_name, dest_storage):
        pass

class RemoteStorage(Storage):

    @abstractmethod
    def download(self, file_info, dest):
        pass

    @abstractmethod
    def upload(self, src, folder_name, file_name, checksum):
        pass

