#!/usr/bin/env python

import os, sys
import urllib2

# Load third party dependencies, check in /libs folder if you've installed them there
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/libs')
from modules.storage import Storage
from modules.config import Config
from modules.flickr_storage import FlickrStorage
from modules.local_storage import LocalStorage
from modules.tree_walker import TreeWalker
from modules.csv_walker import CsvWalker

if __name__ == "__main__":
    try:
        config = Config()
        config.read()

        if config.list_only:
            if config.src.lower() == Config.PATH_FLICKR:
                storage = FlickrStorage(config)
            else:
                storage = LocalStorage(config, config.src)
            if config.list_format == Config.LIST_FORMAT_TREE:
                walker = TreeWalker(config, storage)
            elif config.list_format == Config.LIST_FORMAT_CSV:
                walker = CsvWalker(config, storage)
            else:
                raise ValueError('Unrecognised value for --list-format: {}'.format(config.list_format))

            walker.walk()

    except urllib2.URLError:
        print "Network connection interrupted"
        sys.exit()
    except KeyboardInterrupt:
        sys.exit()
