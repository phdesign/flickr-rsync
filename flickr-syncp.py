#!/usr/bin/env python

import os, sys

# Load third party dependencies, check in /libs folder if you've installed them there
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/libs')
from modules.storage import Storage
from modules.config import Config
from modules.flickr_storage import FlickrStorage
from modules.sample_storage import SampleStorage
from modules.tree_walker import TreeWalker

if __name__ == "__main__":
    try:
        config = Config()
        config.read()

        storage = FlickrStorage(config)
        tree_walker = TreeWalker(storage)
        tree_walker.walk()
    except KeyboardInterrupt:
        sys.exit()
