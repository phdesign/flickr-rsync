import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/libs')
import flickr_api
from flickr_api.api import flickr
import ConfigParser

class Config(object):

    def read(self):
        config = ConfigParser.SafeConfigParser()
        config.read(os.path.splitext(os.path.abspath(__file__))[0] + ".ini")

        self.flickr = dict(config.items('Flickr'))

class Program(object):
    
    def main(self):
        config = Config()
        config.read()

        flickr_api.set_keys(api_key = config.flickr['api_key'], api_secret = config.flickr['api_secret'])

        print flickr.reflection.getMethodInfo(method_name = "flickr.photos.getInfo")
        # flickr_api.set_auth_handler(filename)
        # user = flickr_api.test.login()
        # print user

        print "done"

if __name__ == "__main__":
    Program().main()
