import os, sys
import webbrowser
import ConfigParser

# Load third party dependencies, check in /libs folder if you've installed them there
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/libs')
import flickr_api
from flickr_api.api import flickr
from flickr_api.objects import Photoset, Photo

class Config(object):

    def read(self):
        config = ConfigParser.SafeConfigParser()
        config.read(os.path.splitext(os.path.abspath(__file__))[0] + ".ini")

        self.flickr = dict(config.items('Flickr'))
        self.paths = dict(config.items('Paths'))

class Storage(object):

    def list_folders(self):
        pass

    def list_files(self, folder):
        pass

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

        token_file = os.path.abspath(self._config.paths['token'])
        flickr_api.set_keys(api_key = self._config.flickr['api_key'], api_secret = self._config.flickr['api_secret'])

        if os.path.isfile(token_file):
           auth_handler = flickr_api.auth.AuthHandler.load(token_file) 

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

class Program(object):
    
    def main(self):
        config = Config()
        config.read()

        remote = RemoteStorage(config)
        folders = remote.list_folders()
        # folders = [
            # Photoset(id=1, title="abc")
        # ]
        # folders_str = '\n'.join(map(lambda x: x.title, filter(lambda x: type(x) is Photoset, folders))) 
        folders_str = '\n'.join([x.title for x in folders if type(x) is Photoset]) 
        print folders_str
        
        files = remote.list_files(folders[1])
        print "%r" % files
        # print '\n'.join([x.title for x in files if type(x) is Photo])

        print "Done."

if __name__ == "__main__":
    Program().main()
