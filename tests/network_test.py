# -*- coding: utf-8 -*-
import os, sys
import unittest
import urllib2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libs')
from mock import MagicMock, patch, call
from flickr_rsync.flickr_storage import Network

class NetworkTest(unittest.TestCase):

    def test_should_make_remote_call(self):
        config = MagicMock()
        callback = MagicMock()
        network = Network(config)

        network.call(callback, 'a', b='b')

        callback.assert_called_once_with('a', b='b')

    def test_should_retry_once_with_backoff(self):
        self._call_count = 0
        def throw_one_error():
            if self._call_count == 0:
                return urllib2.URLError('Bang!')
            self._call_count += 1

        config = MagicMock()
        callback = MagicMock()
        callback.side_effect = throw_one_error()
        network = Network(config)

        network.call(callback, 'a', b='b')

        callback.assert_called_once_with('a', b='b')
        pass

    def test_should_retry_specified_times(self):
        pass

    def test_should_fail_once_retry_exceeded(self):
        pass

    def test_should_throttle_consecutive_calls(self):
        pass

    def test_should_not_throttle_if_timeout_passed(self):
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)

