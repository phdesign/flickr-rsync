# flickr-rsync

> Its like rsync for Flickr!

A python script to manage synchronising a local directory of photos with Flickr based on an rsync interaction pattern.

## Installation

Run the following to install flickr-rsync globally (or append `--user` to install for just the current user)
```
$ python setup.py install
```

### Standalone installation

Alternatively, install the dependencies in project folder
```
$ make init
```

And run with
```
$ python flickr_rsync <options>
```

## Authenticating with Flickr

Two keys are provided by Flickr, an api key and a secret. To make your application aware of these keys there are two methods:
* provide `--api-key` and `--api-secret` arguments to the command line
* create a config file in $HOME/.flickr-rsync.ini with the following entries

```
API_KEY = xxxxxxxxxxxxxxxxxxx
API_SECRET = yyyyyyyyyyyyyy
```

where x's and y's are replaced by the values provided by Flickr.

## Listing files

The `--list-only` flag will print a list of files in the source storage provider, this can either be Flickr by specifying the `src` as `Flickr` or a local file system path. Use `--sort-files` to sort the files alphabetically. This feature is useful for manually creating a diff between your local files and Flickr files.

e.g. List all files in Flickr photo sets

```
$ flickr-rsync flickr --list-only
```

Or List all files in a local folder

```
$ flickr-rsync ~/Pictures --list-only
```

### Tree view vs. csv view

You can change the output from a tree view to a comma separated values view by using `--list-format=tree` or `--list-format=csv`. By default the tree view is used.

e.g. Print in tree format

```
$ flickr-rsync flickr --list-only --list-format=tree

├─── 2017-04-24 Family Holiday
│   ├─── IMG_2546.jpg [70ebf9]
│   ├─── IMG_2547.jpg [3d3046]
│   ├─── IMG_2548.jpg [2f2385]
│   └─── IMG_2549.jpg [d8e946]
│   
└─── 2017-04-16 Easter Camping
    ├─── IMG_2515.jpg [aabe74]
    ├─── IMG_2516.jpg [0eb4f2]
    └─── IMG_2517.jpg [4fe908]
```

Or csv format

```
$ flickr-rsync flickr --list-only --list-format=csv

Folder, Filename, Checksum
2017-04-24 Family Holiday, IMG_2546.jpg, 70ebf9be4d8301e94c65582977332754
2017-04-24 Family Holiday, IMG_2547.jpg, 3d3046b37ba338793a762ab7bd83e85c
2017-04-24 Family Holiday, IMG_2548.jpg, 2f23853abeb742551043a3514ba4315b
2017-04-24 Family Holiday, IMG_2549.jpg, d8e946e73700b9c2890d3681c3c0fa0b
2017-04-16 Easter Camping, IMG_2515.jpg, aabe74b06c3a53e801893347eb6bd7f5
2017-04-16 Easter Camping, IMG_2516.jpg, 0eb4f2519f6562ff66069618637a7b10
2017-04-16 Easter Camping, IMG_2517.jpg, 4fe9085b9f320a67988f84e85338a3ff
```

## Syncing files

e.g. To copy all files from Flickr to a local folder

```
$ flickr-rsync flickr ~/Pictures/flickr
```

Or to copy all files from a local folder up to Flickr	

```
$ flickr-rsync ~/Pictures/flickr flickr
```

You can even copy from a local folder to another local folder

```
$ flickr-rsync ~/Pictures/from ~/Pictures/to
```

Files are matched by folder names and file names. E.g. if you have a Flickr photoset called `2017-04-16 Easter Camping` and a file called `IMG_2517.jpg`, and you are trying to copy from a folder with `2017-04-16 Easter Camping\IMG_2517.jpg` it will assume this file is the same and will not try to copy it.

### Will never delete!

`flickr-rsync` will never delete any files, either from Flickr or your local system, it is append only. It will not overwrite any files either, if a file with the same name exists in the same photoset / folder, it will be skipped.

## Filtering

Filtering is done using regular expressions. The following four options control filtering the files:

* `--include=` specifies a pattern that **file paths** must match to be included in the operation
* `--include-dir=` specifies a pattern that **folder names** must match to be included in the operation
* `--exclude=` specifies a pattern that **file paths** must NOT match to be included in the operation
* `--exclude-dir=` specifies a pattern that **folder names** must NOT match to be included in the operation

Note that filtering by folders is more performant than by file paths, prefer folder name filtering where possible.

Also note that exclude filters take preference and will override include filters.

### Root files

Note that filtering does not apply to root files, root files (files in the target folder if local file system, or files not in a photoset on Flickr) are excluded by default. To include them, use `--root-files`.

## Options

All options can be provided by either editing the config file `flickr-rsync.ini` or using the command line interface.

```
usage: flickr-rsync [-h] [-l] [--list-format {tree,csv}] [--list-sort]
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
  -c, --checksum        calculate file checksums for local files. Print
                        checksum when listing, use checksum for comparison
                        when syncing
  --include REGEX       include only files matching REGEX. Defaults to
                        media file extensions only
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

### Config and token file discovery

The config file `flickr-rsync.ini` and Flickr token file `flickr-rsync.token` are searched for in the following locations in order:
* `<current working dir>/flickr-rsync.ini`
* `<current working dir>/.flickr-rsync.ini`
* `<users home dir>/flickr-rsync.ini`
* `<users home dir>/.flickr-rsync.ini`
* `<executable dir>/flickr-rsync.ini`
* `<executable dir>/.flickr-rsync.ini`

## Developing

Either install using the 'standalone' method or install in development mode so source files are symlinked
```
$ python setup.py develop
```

Then to uninstall
```
$ python setup.py develop --uninstall
```

## Running tests

```
$ python setup.py test -q
```
Or
```
$ python -m unittest discover -s tests -p '*_test.py'
```
Or
```
$ make test
```

## Tips

To list just root files only:
```
$ flickr-rsync flickr --exclude-dir '.*' --root-files --list-only
```

## Troubleshooting

#### I get a Version conflict error with the six python package when installing on my Mac

If you're running Mac OSX El Capitan and you get the following error when running `python setup.py test`

```
pkg_resources.VersionConflict: (six 1.4.1 (/System/Library/Frameworks/Python.fra
mework/Versions/2.7/Extras/lib/python), Requirement.parse('six>=1.9'))
```

Do the following:
```
$ sudo pip install --ignore-installed six
```

More details [https://github.com/pypa/pip/issues/3165](https://github.com/pypa/pip/issues/3165)

#### I get an error 'The Flickr API keys have not been set'

To access Flickr this application needs API keys, go to http://www.flickr.com/services/apps/create/apply to sign up for a free personal API key

#### I get an error 'The Flickr API keys have not been set' but I've set them in my config (ini) file

Getting an error `The Flickr API keys have not been set` but you've set them in the config file? Perhaps the application can't find the config file location. Use `-v` or `--verbose` option to print the location of the config file being used.

#### Why are some files are not being shown in the file list / sync?

By default only media files are included in file listings and sync operations. Media files are defined as `\.(jpg|jpeg|png|gif|tiff|tif|bmp|psd|svg|raw|wmv|avi|mov|mpg|mp4|3gp|ogg|ogv|m2ts)$`. Use `--include=.*` to include all files.

### I get an error 'The filename, directory name or volume label syntax is incorrect'

If you're seeing an error like this

```
WindowsError: [Error 123] The filename, directory name, or volume label syntax is incorrect: 'C:\\Users\\xxx\\Pictures" --list-only/*.*'
```

Ensure that you are not using single quotes `'` around a folder path in windows, instead use double quotes `"`. e.g.

```
$ flickr-rsync "C:\Users\xxx\Pictures" --list-only
```



## TODO

* Handle nested directories (merge with separator)
* List duplicate files
* Use checksum matching to avoid uploading duplicate files
* Multi-threading
* Use search to make a filtered lokup faster, is this even possible?
* Webpage for successful Flickr login
* Optimise - why does sort files seem to run faster?!
* Fix duplicate albums issue
* Windows redirect to file encoding issue
