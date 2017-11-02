#!/usr/bin/env python

"""
Python setuptools install script.
Run with "python setup.py install" to install FlickrAPI
"""

from __future__ import print_function
import os, sys
import unittest

# Check the Python version
(major, minor) = sys.version_info[:2]
if (major, minor) < (2, 7) or (major == 3 and minor < 3):
    raise SystemExit("Sorry, Python 2.7, or 3.3 or newer required")

# Load version number into __version__
execfile('flickr_rsync/_version.py')

from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

def test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='*_test.py')
    return test_suite

additional_requires = []
if os.name == 'nt':
    additional_requires.append('win_unicode_console~=0.5')

setup(
    name='flickr-rsync',
    version=__version__,
    description='A python script to manage synchronising a local directory of photos with flickr based on an rsync interaction pattern',
    long_description=readme(),
    author='Paul Heasley',
    author_email='paul@phdesign.com.au',
    url='http://www.phdesign.com.au/flickr-rsync',
    download_url='https://github.com/phdesign/flickr-rsync/archive/v{}.tar.gz'.format(__version__),
    packages=['flickr_rsync'],
    license='MIT',
    keywords=['flickr', 'sync', 'rsync'],
    classifiers='',
    install_requires=[
        'flickr_api>=0.5beta',
        'argparse~=1.4.0',
        'rx~=1.5.9',
        'futures~=3.1.1',
        'backoff~=1.3.1'
    ] + additional_requires,
    dependency_links = [
      'https://github.com/alexis-mignon/python-flickr-api/tarball/6f3163b#egg=flickr_api-0.5beta'
    ],
    tests_require=[
        'mock~=2.0.0'
    ],
    test_suite='setup.test_suite',
    zip_safe=True,
    entry_points = {
        'console_scripts': ['flickr-rsync=flickr_rsync:main'],
    },
    include_package_data=True
)
