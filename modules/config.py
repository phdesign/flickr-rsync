import os
import __main__
import ConfigParser
import argparse
from distutils.util import strtobool

FILES_SECTION = 'Files'
FLICKR_SECTION = 'Flickr'
NETWORK_SECTION = 'Network'
OPTIONS_SECTION = 'Options'

DEFAULTS = {
    'src': '',
    'dest': '',
    'list_only': False,
    'list_format': 'tree',
    'include': '\.(jpg|png|avi|mov|mpg|mp4|3gp)$',
    'include_dir': '',
    'exclude': '',
    'exclude_dir': '',
    'root_files': False,
    'dry_run': False,
    'throttling': 0.5,
    'retry': 7,
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

    def __getattr__(self, name):
        # Thanks: http://stackoverflow.com/questions/26467564/how-to-copy-all-attributes-of-one-python-object-to-another
        return getattr(self._args, name)

    def read(self):
        parser = argparse.ArgumentParser(description='A python script to manage synchronising a local directory of photos to flickr', prog='flickr-syncp')
        parser.add_argument('src', type=str, nargs='?', 
                            help='the source directory to copy or list files from, or FLICKR to specify flickr')
        parser.add_argument('dest', type=str, nargs='?', 
                            help='the destination directory to copy files to, or FLICKR to specify flickr')
        parser.add_argument('-l', '--list-only', action='store_true',
                            help='list the files in --src instead of copying them')
        parser.add_argument('--list-format', choices=[self.LIST_FORMAT_TREE, self.LIST_FORMAT_CSV],
                            help='output format for --list-only, TREE for a tree based output or CSV')
        parser.add_argument('--include', type=str, metavar='REGEX',
                            help='include only files matching REGEX')
        parser.add_argument('--include-dir', type=str, metavar='REGEX',
                            help='include only directories matching REGEX ')
        parser.add_argument('--exclude', type=str, metavar='REGEX',
                            help='exclude any files matching REGEX, note this takes precedent over --include')
        parser.add_argument('--exclude-dir', type=str, metavar='REGEX',
                            help='exclude any directories matching REGEX, note this takes precedent over --include-dir')
        parser.add_argument('--root-files', action='store_true',
                            help='includes roots files (not in a directory or a photoset) in the list or copy')
        parser.add_argument('-n', '--dry-run', action='store_true',
                            help='in sync mode, don\'t actually copy anything, just simulate the process and output')
        parser.add_argument('--throttling', type=float, metavar='SEC',
                            help='the delay in seconds (may be decimal) before each network call')
        parser.add_argument('--retry', type=int, metavar='NUM',
                            help='the number of times to retry a network call before failing')
        parser.add_argument('--api-key', type=str,
                            help='flickr API key')
        parser.add_argument('--api-secret', type=str,
                            help='flickr API secret')
        parser.add_argument('--tags', type=str, metavar='"TAG1 TAG2"',
                            help='space seperated list of tags to apply to uploaded files on flickr')
        parser.add_argument('--version', action='version', version='%(prog)s 0.1')
        parser.set_defaults(**self._read_ini())
        self._args = parser.parse_args()

    def _read_ini(self):
        config = ConfigParser.SafeConfigParser()
        ini_path = os.path.splitext(os.path.abspath(__main__.__file__))[0] + '.ini'
        config.read(ini_path)

        options = DEFAULTS.copy()
        self._read_files_section(config, options)
        self._read_network_section(config, options)
        self._read_options_section(config, options)
        self._read_flickr_section(config, options)
        return options

    def _read_options_section(self, config, options):
        if not config.has_section(OPTIONS_SECTION):
            return
        items = dict(config.items(OPTIONS_SECTION))
        if items.get('list_only'):
            items['list_only'] = self._strtobool(items['list_only'])
        if items.get('list_format'):
            items['list_format'] = items['list_format'].lower()
        if items.get('dry_run'):
            items['dry_run'] = self._strtobool(items['dry_run'])
        options.update(items)

    def _read_network_section(self, config, options):
        if not config.has_section(NETWORK_SECTION):
            return
        items = dict(config.items(NETWORK_SECTION))
        if items.get('throttling'):
            items['throttling'] = float(items['throttling'])
        if items.get('retry'):
            items['retry'] = int(items['retry'])
        options.update(items)

    def _read_files_section(self, config, options):
        if not config.has_section(FILES_SECTION):
            return
        items = dict(config.items(FILES_SECTION))
        if items.get('root_files'):
            items['root_files'] = self._strtobool(items['root_files'])
        options.update(items)

    def _read_flickr_section(self, config, options):
        if not config.has_section(FLICKR_SECTION):
            return
        items = dict(config.items(FLICKR_SECTION))
        if items.get('is_public'):
            items['is_public'] = int(items['is_public'])
        if items.get('is_friend'):
            items['is_friend'] = int(items['is_friend'])
        if items.get('is_family'):
            items['is_family'] = int(items['is_family'])
        options.update(items)

    def _strtobool(self, val):
        return bool(strtobool(val))

