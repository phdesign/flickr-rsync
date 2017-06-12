from __future__ import print_function
import os, sys
import ConfigParser
import argparse
from distutils.util import strtobool
from _version import __version__

__packagename__ = 'flickr-rsync'

CONFIG_FILENAME = __packagename__ + '.ini'

FILES_SECTION = 'Files'
FLICKR_SECTION = 'Flickr'
NETWORK_SECTION = 'Network'
OPTIONS_SECTION = 'Options'

DEFAULTS = {
    'src': '',
    'dest': '',
    'list_only': False,
    'list_format': 'tree',
    'list_sort': False,
    'list_folders': False,
    'checksum': False,
    'include': '\.(jpg|jpeg|png|gif|tiff|tif|bmp|psd|svg|raw|wmv|avi|mov|mpg|mp4|3gp|ogg|ogv|m2ts)$',
    'include_dir': '',
    'exclude': '',
    'exclude_dir': '',
    'root_files': False,
    'dry_run': False,
    'throttling': 0.5,
    'retry': 7,
    'api_key': '',
    'api_secret': '',
    'tags': __packagename__,
    'is_public': 0,
    'is_friend': 0,
    'is_family': 0,
    'verbose': False
}

class Config(object):

    LIST_FORMAT_TREE = 'tree'
    LIST_FORMAT_CSV = 'csv'
    PATH_FLICKR = 'flickr'
    PATH_FAKE = 'fake'

    def __getattr__(self, name):
        # Thanks: http://stackoverflow.com/questions/26467564/how-to-copy-all-attributes-of-one-python-object-to-another
        return getattr(self._args, name)

    def read(self):
        parser = argparse.ArgumentParser(description='A python script to manage synchronising a local directory of photos to flickr', prog=__packagename__)
        parser.add_argument('src', type=str, nargs='?', 
                            help='the source directory to copy or list files from, or FLICKR to specify flickr')
        parser.add_argument('dest', type=str, nargs='?', 
                            help='the destination directory to copy files to, or FLICKR to specify flickr')
        parser.add_argument('-l', '--list-only', action='store_true',
                            help='list the files in --src instead of copying them')
        parser.add_argument('--list-format', choices=[self.LIST_FORMAT_TREE, self.LIST_FORMAT_CSV],
                            help='output format for --list-only, TREE for a tree based output or CSV')
        parser.add_argument('--list-sort', action='store_true',
                            help='sort alphabetically when --list-only, note that this forces buffering of remote sources so will be slower')
        parser.add_argument('--list-folders', action='store_true',
                            help='lists only folders (no files, implies --list-only)')
        parser.add_argument('-c', '--checksum', action='store_true',
                            help='calculate file checksums for local files. Print checksum when listing, use checksum for comparison when syncing')
        parser.add_argument('--include', type=str, metavar='REGEX',
                            help='include only files matching REGEX. Defaults to media file extensions only')
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
        parser.add_argument('-v', '--verbose', action='store_true',
                            help='increase verbosity')
        parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
        ini_path = self.locate_datafile(CONFIG_FILENAME)
        parser.set_defaults(**self._read_ini(ini_path))
        self._args = parser.parse_args()
        
        if self.verbose:
            if ini_path:
                print("using config file {}".format(ini_path))
            else:
                print("no config file found")

    def locate_datafile(self, filename):
        def file_locations(filename):
            # Look in working directory
            yield os.path.join(os.getcwd(), filename)
            yield os.path.join(os.getcwd(), '.' + filename)
            # Look in user home folder
            yield os.path.join(os.path.expanduser('~'), filename)
            yield os.path.join(os.path.expanduser('~'), '.' + filename)
            # Look in executable folder
            yield os.path.join(os.path.realpath(sys.argv[0]), filename)
            yield os.path.join(os.path.realpath(sys.argv[0]), '.' + filename)

        for path_to_test in file_locations(filename):
            if os.path.isfile(path_to_test):
                return path_to_test

        return None

    def default_datafile(self, filename):
        return os.path.join(os.path.expanduser('~'), '.' + filename)

    def _read_ini(self, ini_path):
        options = DEFAULTS.copy()
        config = ConfigParser.SafeConfigParser()

        if ini_path:
            config.read(ini_path)
            self._read_files_section(config, options)
            self._read_network_section(config, options)
            self._read_options_section(config, options)
            self._read_flickr_section(config, options)

        return options

    def _read_options_section(self, config, options):
        if not config.has_section(OPTIONS_SECTION):
            return
        items = self._read_section(config, NETWORK_SECTION, {
            'list_only': bool,
            'list_format': lambda item: item.lower(),
            'list_sort': bool,
            'list_folders': bool,
            'checksum': bool,
            'dry_run': bool,
            'verbose': bool
        })
        options.update(items)

    def _read_network_section(self, config, options):
        if not config.has_section(NETWORK_SECTION):
            return
        items = self._read_section(config, NETWORK_SECTION, {
            'throttling': float,
            'retry': int
        })
        options.update(items)

    def _read_files_section(self, config, options):
        if not config.has_section(FILES_SECTION):
            return
        items = self._read_section(config, FILES_SECTION, {
            'root_files': bool    
        })
        options.update(items)

    def _read_flickr_section(self, config, options):
        if not config.has_section(FLICKR_SECTION):
            return
        items = self._read_section(config, FLICKR_SECTION, {
            'is_public': int,
            'is_friend': int,
            'is_family': int
        })
        options.update(items)

    def _read_section(self, config, section, types):
        items = dict(config.items(section))
        for prop, typeinfo in types.iteritems():
            if (items.get(prop)):
                if (typeinfo == int):
                    items[prop] = int(items[prop])
                elif (typeinfo == float):
                    items[prop] = float(items[prop])
                elif (typeinfo == bool):
                    items[prop] = self._strtobool(items[prop])
                elif (callable(typeinfo)):
                    items[prop] = typeinfo(items[prop])
        return items

    def _strtobool(self, val):
        return bool(strtobool(val))

