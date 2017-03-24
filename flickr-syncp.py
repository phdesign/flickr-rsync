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

if __name__ == "__main__":
    try:
        config = Config()
        config.read()

        if config.options['mode'] == 'list':
            if config.options['direction'] == 'local' or config.options['direction'] == 'both':
                storage = LocalStorage(config)
                tree_walker = TreeWalker(storage)
                print "\nLocal"
                tree_walker.walk()

            if config.options['direction'] == 'flickr' or config.options['direction'] == 'both':
                storage = FlickrStorage(config)
                tree_walker = TreeWalker(storage)
                print "\nRemote"
                tree_walker.walk()
    except urllib2.URLError:
        print "Network connection interrupted"
        sys.exit()
    except KeyboardInterrupt:
        sys.exit()
