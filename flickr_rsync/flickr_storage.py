from __future__ import print_function
import os, sys
import re
import webbrowser
import datetime
import logging
from storage import RemoteStorage
import flickr_api
from flickr_api.api import flickr
from file_info import FileInfo
from folder_info import FolderInfo
from local_storage import mkdirp
from config import __packagename__

TOKEN_FILENAME = __packagename__ + '.token'
CHECKSUM_PREFIX = 'checksum:md5'
OAUTH_PERMISSIONS = 'write'
logger = logging.getLogger(__name__)

class FlickrStorage(RemoteStorage):

    def __init__(self, config, resiliently):
        self._config = config
        self._resiliently = resiliently
        self._is_authenticated = False
        self._user = None
        self._photosets = {}
        self._photos = {}

    def list_folders(self):
        """
        Lists all photosets in Flickr

        Returns:
            A lazy loaded generator function of FolderInfo objects
        """
        self._authenticate()

        walker = self._resiliently.call(flickr_api.objects.Walker, self._user.getPhotosets)
        for photoset in walker:
            self._photosets[photoset.id] = photoset
            folder = FolderInfo(id=photoset.id, name=photoset.title.encode('utf-8'))
            if self._should_include(folder.name, self._config.include_dir, self._config.exclude_dir):
                yield folder

    def list_files(self, folder):
        """
        Lists all photos within a photoset

        Args:
            folder: The FolderInfo object of the folder to list (from list_folders), or None to list all photos not 
                in a photoset

        Returns:
            A lazy loaded generator function of FileInfo objects

        Raises:
            KeyError: If folder.id is unrecognised
        """
        self._authenticate()

        if not folder.is_root:
            walker = self._resiliently.call(
                flickr_api.objects.Walker,
                self._photosets[folder.id].getPhotos,
                extras='original_format,tags')
        else:
            walker = self._resiliently.call(
                flickr_api.objects.Walker,
                self._user.getNotInSetPhotos,
                extras='original_format,tags')

        for photo in walker:
            self._photos[photo.id] = photo
            file_info = self._get_file_info(photo)
            if self._should_include(file_info.name, self._config.include, self._config.exclude):
                yield file_info

    def download(self, file_info, dest_path):
        """
        Downloads a photo from Flickr to local file system

        Args:
            file_info: The file info object (as returned by list_files) of the file to download
            dest_path: The file system path to save the file to

        Raises:
            KeyError: If the file_info.id is unrecognised
        """
        mkdirp(dest_path)
        photo = self._photos[file_info.id]
        self._resiliently.call(photo.save, dest_path, size_label='Original')

    def upload(self, src_path, folder_name, file_name, checksum):
        """
        Uploads a photo to Flickr from local file system

        Args:
            src_path: The file system path to upload the photo from
            folder_name: The photset name to add the photo to
            file_name: The name of the photo, any extension will be removed

        Raises:
            KeyError: If the file_info.id is unrecognised
        """
        tags = self._config.tags
        if checksum:
            tags = '{} {}={}'.format(tags, CHECKSUM_PREFIX, checksum)

        photo = self._resiliently.call(
            flickr_api.upload,
            photo_file=src_path, 
            title=os.path.splitext(file_name)[0], 
            tags=tags.strip(),
            is_public=self._config.is_public,
            is_friend=self._config.is_friend,
            is_family=self._config.is_family,
            async=0)

        if folder_name:
            photoset = self._get_folder_by_name(folder_name)
            if not photoset:
                photoset = self._resiliently.call(flickr_api.Photoset.create, title=folder_name, primary_photo=photo)
                self._photosets[photoset.id] = photoset
            else:
                self._resiliently.call(photoset.addPhoto, photo=photo)

    def copy_file(self, file_info, folder_name, dest_storage):
        if isinstance(dest_storage, RemoteStorage):
            temp_file = NamedTemporaryFile()
            self.download(file_info, temp_file.name)
            dest_storage.upload(temp_file.name, folder_name, file_info.name, file_info.checksum)
            temp_file.close()
        else:
            dest = os.path.join(dest_storage.path, folder_name, file_info.name)
            self.download(file_info, dest)

    def _get_folder_by_name(self, name):
        return next((x for x in self._photosets.values() if x.title.encode('utf-8').lower() == name.lower()), None)

    def _get_file_info(self, photo):
        name = photo.title.encode('utf-8') if photo.title else photo.id
        checksum = None
        if photo.originalformat:
            name += "." + photo.originalformat
        if photo.tags:
            tags = photo.tags.split()
            checksum = next((parts[1] for parts in (tag.split('=') for tag in tags) if parts[0] == CHECKSUM_PREFIX), None)
        return FileInfo(id=photo.id, name=name, checksum=checksum)

    def _should_include(self, name, include_pattern, exclude_pattern):
        return ((not include_pattern or re.search(include_pattern, name, flags=re.IGNORECASE)) and
            (not exclude_pattern or not re.search(exclude_pattern, name, flags=re.IGNORECASE)))

    def _authenticate(self):
        if self._is_authenticated:
            return

        flickr_api.set_keys(api_key = self._config.api_key, api_secret = self._config.api_secret)

        token_path = self._config.locate_datafile(TOKEN_FILENAME)
        if token_path:
           auth_handler = flickr_api.auth.AuthHandler.load(token_path) 

        else:
            token_path = self._config.default_datafile(TOKEN_FILENAME)
            auth_handler = flickr_api.auth.AuthHandler()
            permissions_requested = OAUTH_PERMISSIONS
            url = auth_handler.get_authorization_url(permissions_requested)
            webbrowser.open(url)
            print("Please enter the OAuth verifier tag once logged in:")
            verifier_code = raw_input("> ")
            auth_handler.set_verifier(verifier_code)
            auth_handler.save(token_path)

        try:
            flickr_api.set_auth_handler(auth_handler)
            self._user = flickr_api.test.login()
            self._is_authenticated = True

        except flickr_api.flickrerrors.FlickrError as e:
            print(e.message)
            if e.message == 'The Flickr API keys have not been set':
                print("Go to http://www.flickr.com/services/apps/create/apply and apply for an API key")
            sys.exit(1);
