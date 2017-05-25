# flickr-syncp

A python script to manage synchronising a local directory of photos with flickr based on an rsync interaction pattern

## Installation

Run the following to install dependencies locally within the package directory
```
pip install flickr_api --target ./libs
```

## Running from config

Edit the `flickr-syncp.ini` file.

Run the flickr-syncp.py file, e.g.
```
python flickr-syncp.py
```

## Running from CLI
```
# Listing files
python flickr-syncp.py --mode list --src flickr --include .* --include-dir .* --exclude \.gitignore --exclude-dir \.git

# Copying files
python flickr-syncp.py --mode sync --src /Users/paul/Pictures/Uploadr/ --dest flickr

# To list just root files
python flickr-syncp.py flickr --exclude-dir '.*' --root-files --list-only
```

### Options
```
usage: flickr-syncp [-h] [-l] [--list-format {tree,csv}] [--list-sort]
                    [--include REGEX] [--include-dir REGEX] [--exclude REGEX]
                    [--exclude-dir REGEX] [--root-files] [-n]
                    [--throttling SEC] [--retry NUM] [--api-key API_KEY]
                    [--api-secret API_SECRET] [--tags "TAG1 TAG2"] [-v]
                    [--version]
                    [src] [dest]

A python script to manage synchronising a local directory of photos to flickr

positional arguments:
  src                   the source directory to copy or list files from, or
                        FLICKR to specify flickr
  dest                  the destination directory to copy files to, or FLICKR
                        to specify flickr

optional arguments:
  -h, --help            show this help message and exit
  -l, --list-only       list the files in --src instead of copying them
  --list-format {tree,csv}
                        output format for --list-only, TREE for a tree based
                        output or CSV
  --list-sort           sort alphabetically when --list-only, note that this
                        forces buffering of remote sources so will be slower
  --include REGEX       include only files matching REGEX
  --include-dir REGEX   include only directories matching REGEX
  --exclude REGEX       exclude any files matching REGEX, note this takes
                        precedent over --include
  --exclude-dir REGEX   exclude any directories matching REGEX, note this
                        takes precedent over --include-dir
  --root-files          includes roots files (not in a directory or a
                        photoset) in the list or copy
  -n, --dry-run         in sync mode, don't actually copy anything, just
                        simulate the process and output
  --throttling SEC      the delay in seconds (may be decimal) before each
                        network call
  --retry NUM           the number of times to retry a network call before
                        failing
  --api-key API_KEY     flickr API key
  --api-secret API_SECRET
                        flickr API secret
  --tags "TAG1 TAG2"    space seperated list of tags to apply to uploaded
                        files on flickr
  -v, --verbose         increase verbosity
  --version             show program's version number and exit
```

## TODO

* Handle nested directories (merge with separator)
* --add-checksum-ta*g (Add checksumto all files)
* --list-duplicates
* Copy local files / add to multiple albums if checksum equal. (How to deal with same file different names)
* Multi-threading
* Fix unicode characters on Windows
* Allow search?
* If no API key, list flickr URL to signup
* Webpage for successfullFlickr login
* Use a RootFolderInfo instead of None for root folder
