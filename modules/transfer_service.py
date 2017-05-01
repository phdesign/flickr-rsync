from tempfile import NamedTemporaryFile
from flickr_storage import FlickrStorage
from local_storage import LocalStorage

class TransferService(object):

    def copy_file(file_info, src_storage, folder_name, dest_storage):

        if isinstance(dest_storage, LocalStorage):
            dest_path = os.path.join(dest_storage.path, folder_name, file_info.name)
        elif isinstance(dest_storage, FlickrStorage):
            temp_file = NamedTemporaryFile()
            dest_path = temp_file.name
        else:
            raise NotImplementedError()

        if isinstance(src_storage, LocalStorage):
            src_storage.copy_file(file_info, dest_path)
        elif isinstance(src_storage, FlickrStorage):
            src_storage.download(file_info, dest_path)
        else:
            raise NotImplementedError()

        if isinstance(dest_storage, LocalStorage):
            # We're done
            pass
        elif isinstance(dest_storage, FlickrStorage):
            dest_storage.upload(dest_path, folder_name, file_name)
            if temp_file:
                temp_file.close()
        else:
            raise NotImplementedError()


