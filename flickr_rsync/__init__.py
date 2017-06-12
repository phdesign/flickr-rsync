from __future__ import print_function
import os, sys
import urllib2

# Load third party dependencies, check in /libs folder if you've installed them there
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '../libs')

import verbose as verbose
from storage import Storage
from config import Config
from sync import Sync
from flickr_storage import FlickrStorage
from local_storage import LocalStorage
from fake_storage import FakeStorage
from tree_walker import TreeWalker
from csv_walker import CsvWalker

def _get_storage(config, path):
    if path.lower() == Config.PATH_FLICKR:
        return FlickrStorage(config)
    elif path.lower() == config.PATH_FAKE:
        return FakeStorage(config)
    return LocalStorage(config, path)

def _get_walker(config, storage, list_format):
    if list_format == Config.LIST_FORMAT_TREE:
        return TreeWalker(config, storage)
    elif list_format == Config.LIST_FORMAT_CSV:
        return CsvWalker(config, storage)
    else:
        raise ValueError('Unrecognised value for list-format: {}'.format(list_format))

def patch_win_unicode():
    if os.name == 'nt':
        import win_unicode_console
        win_unicode_console.enable()

def main():
    patch_win_unicode()
    try:
        config = Config()
        config.read()
        verbose.set_config(config)

        src_storage = _get_storage(config, config.src)
        if config.list_only or config.list_folders:
            walker = _get_walker(config, src_storage, config.list_format)
            walker.walk()
        else:
            dest_storage = _get_storage(config, config.dest)
            sync = Sync(config, src_storage, dest_storage)
            sync.run()

    except urllib2.URLError as e:
        print("Error connecting to server. {}".format(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit()
