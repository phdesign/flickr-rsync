import os
import __main__
import ConfigParser

class Config(object):

    def read(self):
        config = ConfigParser.SafeConfigParser()
        ini_path = os.path.splitext(os.path.abspath(__main__.__file__))[0] + '.ini'
        config.read(ini_path)

        self.flickr = dict(config.items('Flickr'))
        self.network = dict(config.items('Network'))
        self.paths = dict(config.items('Paths'))
