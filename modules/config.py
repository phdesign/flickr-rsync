import os
import __main__
import ConfigParser

FILES_SECTION = 'Files'
FLICKR_SECTION = 'Flickr'
NETWORK_SECTION = 'Network'
OPTIONS_SECTION = 'Options'

DEFAULT_FLICKR = {
    'api_key': '',
    'api_secret': '',
    'tags': 'flickr-syncp',
    'is_public': 0,
    'is_friend': 0,
    'is_family': 0
}

class Config(object):

    LIST_FORMAT_TREE = 'tree'
    LIST_FORMAT_CSV = 'csv'
    PATH_FLICKR = 'flickr'

    def __init__(self):
        self.src = ''
        self.dest = ''
        self.list_only = True
        self.list_format = 'tree'
        self.include = '\.(jpg|png|avi|mov|mpg|mp4|3gp)$'
        self.include_dir = ''
        self.exclude = ''
        self.exclude_dir = ''
        self.dry_run = False
        self.throttling = 0.5
        self.retry = 7
        self.flickr = {}

    def read(self):
        config = ConfigParser.SafeConfigParser()
        ini_path = os.path.splitext(os.path.abspath(__main__.__file__))[0] + '.ini'
        config.read(ini_path)

        self._read_files_section(config)
        self._read_network_section(config)
        self._read_options_section(config)
        self.flickr = self._read_section(config, FLICKR_SECTION, DEFAULT_FLICKR)

    def _read_section(self, config, section, default):
        if not config.has_section(section):
            return default
        merged = default.copy()
        merged.update(config.items(section))
        return merged

    def _read_options_section(self, config):
        if not config.has_section(OPTIONS_SECTION):
            return
        if config.has_option(OPTIONS_SECTION, 'list_only'):
            self.list_only = config.getboolean(OPTIONS_SECTION, 'list_only')
        if config.has_option(OPTIONS_SECTION, 'list_format'):
            self.list_format = config.get(OPTIONS_SECTION, 'list_format').lower()

    def _read_network_section(self, config):
        if not config.has_section(NETWORK_SECTION):
            return
        if config.has_option(NETWORK_SECTION, 'throttling'):
            self.throttling = float(config.get(NETWORK_SECTION, 'throttling'))
        if config.has_option(NETWORK_SECTION, 'retry'):
            self.retry = config.getint(NETWORK_SECTION, 'retry')

    def _read_files_section(self, config):
        if not config.has_section(FILES_SECTION):
            return
        if config.has_option(FILES_SECTION, 'src'):
            self.src = config.get(FILES_SECTION, 'src')
        if config.has_option(FILES_SECTION, 'dest'):
            self.dest = config.get(FILES_SECTION, 'dest')
        if config.has_option(FILES_SECTION, 'include'):
            self.include = config.get(FILES_SECTION, 'include')
        if config.has_option(FILES_SECTION, 'include_dir'):
            self.include_dir = config.get(FILES_SECTION, 'include_dir')
        if config.has_option(FILES_SECTION, 'exclude'):
            self.exclude = config.get(FILES_SECTION, 'exclude')
        if config.has_option(FILES_SECTION, 'exclude_dir'):
            self.exclude_dir = config.get(FILES_SECTION, 'exclude_dir')
        if config.has_option(FILES_SECTION, 'root_files'):
            self.root_files = config.getboolean(FILES_SECTION, 'root_files')

