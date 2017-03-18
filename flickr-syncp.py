#!/usr/bin/env python

import os, sys

# Load third party dependencies, check in /libs folder if you've installed them there
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/libs')
from pack.storage import Storage
from pack.config import Config
from pack.remote_storage import RemoteStorage
from pack.sample_storage import SampleStorage
from pack.tree_walker import TreeWalker

if __name__ == "__main__":
    try:
        config = Config()
        config.read()

        storage = RemoteStorage(config)
        tree_walker = TreeWalker(storage)
        tree_walker.walk()
    except KeyboardInterrupt:
        sys.exit()
