from abc import abstractmethod

class Storage(object):

    @abstractmethod
    def list_folders(self):
        pass

    @abstractmethod
    def list_files_in_folder(self, folder):
        pass

    @abstractmethod
    def copy_file(self, file_info, folder_name, dest_storage):
        pass

    @abstractmethod
    def receive_file(self, file_info, folder_name):
        pass

