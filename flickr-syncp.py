#!/usr/bin/env python
from __future__ import print_function
import os, sys
import urllib2

# Load third party dependencies, check in /libs folder if you've installed them there
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/libs')
from modules.storage import Storage
from modules.config import Config
from modules.sync import Sync
from modules.flickr_storage import FlickrStorage
from modules.local_storage import LocalStorage
from modules.tree_walker import TreeWalker
from modules.csv_walker import CsvWalker

def _get_storage(config, path):
    if path.lower() == Config.PATH_FLICKR:
        return FlickrStorage(config)
    return LocalStorage(config, path)

def _get_walker(config, storage, list_format):
    if list_format == Config.LIST_FORMAT_TREE:
        return TreeWalker(config, storage)
    elif list_format == Config.LIST_FORMAT_CSV:
        return CsvWalker(config, storage)
    else:
        raise ValueError('Unrecognised value for list-format: {}'.format(list_format))

if __name__ == "__main__":
    try:
        config = Config()
        config.read()

        src_storage = _get_storage(config, config.src)
        if config.list_only:
            walker = _get_walker(config, src_storage, config.list_format)
            walker.walk()
        else:
            dest_storage = _get_storage(config, config.dest)
            sync = Sync(config, src_storage, dest_storage)
            sync.run()

    except urllib2.URLError:
        print("Network connection interrupted")
        sys.exit()
    except KeyboardInterrupt:
        sys.exit()
