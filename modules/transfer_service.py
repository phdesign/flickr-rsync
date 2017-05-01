from tempfile import NamedTemporaryFile
from flickr_storage import FlickrStorage
from local_storage import LocalStorage

class TransferService(object):

    def copy_file(file_info, src_storage, folder_name, dest_storage):

        if isinstance(src_storage, LocalStorage):
            src = file_info.full_path
            if isinstance(dest_storage, LocalStorage):
                dest = os.path.join(dest_storage.path, folder_name, file_info.name)
                dest_storage.copy_file(src, dest)

            elif isinstance(dest_storage, FlickrStorage):
                dest_storage.upload(src_path, folder_name, file_info.name)

        elif isinstance(src_storage, FlickrStorage):
            if isinstance(dest_storage, LocalStorage):
                dest = os.path.join(dest_storage.path, folder_name, file_info.name)
                src_storage.download(file_info, dest)

            elif isinstance(dest_storage, FlickrStorage):
                temp_file = NamedTemporaryFile()
                src_storage.download(file_info, temp_file.name)
                dest_storage.upload(temp_file.name, folder_name, file_info.name)
                temp_file.close()

