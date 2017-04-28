# flickr-syncp

A python script to manage synchronising a local directory of photos to flickr

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
```

### Options
```
        --src               the source directory to copy or list files from, or FLICKR to specify flickr
        --dest              the destination directory to copy files to, or FLICKR to specify flickr
        --list-only         list the files in --src instead of copying them
        --list-format       output format for --list-only, TREE for a tree based output or CSV
        --include           include only files matching REGEX
        --include-dir       include only directories matching REGEX 
        --exclude           exclude any files matching REGEX, note this takes precedent over --include
        --exclude-dir       exclude any directories matching REGEX, note this takes precedent over --include-dir
        --root-files        includes roots files (not in a directory or a photoset) in the list or copy
        --recursive         recurses into subdirectories and treats them as photosets, prefixing the name with the parent
                            folder name
    -n, --dry-run           in sync mode, don't actually copy anything, just simulate the process and output
        --max-size          don't transfer any file larger than SIZE
        --version           print version number
    -h, --help              show this help
```

## TODO

* How to handle nested directories (merge with separator)
