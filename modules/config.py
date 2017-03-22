import os
import __main__
import ConfigParser

DEFAULT_FLICKR = {
    'api_key': '',
    'api_secret': '',
    'tags': 'flickr-syncp',
    'is_public': 0,
    'is_friend': 0,
    'is_family': 0
}
DEFAULT_NETWORK = {
    'throttling': 0.5,
    'retry': 7
}
DEFAULT_FILES = {
    'files_dir': '',
    'local_file_types': '*.jpg,*.png,*.avi,*.mov,*.mpg,*.mp4,*.3gp',
    'local_exclude': '',
    'remote_exclude': ''
}

class Config(object):

    def read(self):
        config = ConfigParser.SafeConfigParser()
        ini_path = os.path.splitext(os.path.abspath(__main__.__file__))[0] + '.ini'
        config.read(ini_path)

        self.flickr = self._read_section(config, 'Flickr', DEFAULT_FLICKR)
        self.network = self._read_section(config, 'Network', DEFAULT_NETWORK)
        self.files = self._read_section(config, 'Files', DEFAULT_FILES)

    def _read_section(self, config, section, default):
        if not config.has_section(section):
            return default
        merged = default.copy()
        merged.update(config.items(section))
        return merged

