import os
import __main__
import webbrowser
from storage import Storage
import flickr_api
from flickr_api.api import flickr

class RemoteStorage(Storage):

    def __init__(self, config):
        self._config = config
        self._is_authenticated = False
        self._user = None

    def list_folders(self):
        self._authenticate()
        photo_sets = self._user.getPhotosets()
        return photo_sets

    def list_files(self, folder):
        self._authenticate()
        photos = folder.getPhotos()
        return photos
        # return photos[0].getInfo()

    def _authenticate(self):
        if self._is_authenticated:
            return

        flickr_api.set_keys(api_key = self._config.flickr['api_key'], api_secret = self._config.flickr['api_secret'])

        token_path = self._config.paths['token']
        if not os.path.isabs(token_path):
            token_path = os.path.join(os.path.abspath(os.path.dirname(__main__.__file__)), token_path)
        if os.path.isfile(token_path):
           auth_handler = flickr_api.auth.AuthHandler.load(token_path) 

        else:
            auth_handler = flickr_api.auth.AuthHandler()
            permissions_requested = "read"
            url = auth_handler.get_authorization_url(permissions_requested)
            webbrowser.open(url)
            print "Please enter the OAuth verifier tag once logged in:"
            verifier_code = raw_input("> ")
            auth_handler.set_verifier(verifier_code)
            auth_handler.save(token_file)

        flickr_api.set_auth_handler(auth_handler)
        self._user = flickr_api.test.login()
        self._is_authenticated = True
