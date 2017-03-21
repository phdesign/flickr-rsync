#!/usr/bin/env python

import os, sys
import urllib2

# Load third party dependencies, check in /libs folder if you've installed them there
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/libs')
from modules.storage import Storage
from modules.config import Config
from modules.flickr_storage import FlickrStorage
from modules.local_storage import LocalStorage
from modules.sample_storage import SampleStorage
from modules.tree_walker import TreeWalker

if __name__ == "__main__":
    try:
        config = Config()
        config.read()

        storage = LocalStorage(config)
        tree_walker = TreeWalker(storage)
        print "Local"
        tree_walker.walk()
        # sys.exit()

        storage = FlickrStorage(config)
        tree_walker = TreeWalker(storage)
        print
        print "Remote"
        tree_walker.walk()
    except urllib2.URLError:
        print "Network connection interrupted"
        sys.exit()
    except KeyboardInterrupt:
        sys.exit()
