# -*- coding: utf-8 -*-
import os, sys
import unittest
import time
import urllib2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
from mock import MagicMock, patch, call
import helpers
from flickr_rsync.resiliently import Resiliently

class ResilientlyTest(unittest.TestCase):

    def setUp(self):
        self.print_patch = patch('flickr_rsync.throttle.print', create=True)
        self.mock_print = self.print_patch.start()
        self.sleep_patch = patch('flickr_rsync.throttle.time.sleep', create=True)
        self.mock_sleep = self.sleep_patch.start()

        self.config = MagicMock()
        self.callback = MagicMock()
        self.callback.__name__ = 'foo'

    def tearDown(self):
        self.print_patch.stop()
        self.sleep_patch.stop()

    def test_should_make_remote_call(self):
        resiliently = Resiliently(self.config)

        resiliently.call(self.callback, 'a', b='b')

        self.callback.assert_called_once_with('a', b='b')

    def test_should_retry_once_with_backoff(self):
        self.config.retry = 1
        self.callback.side_effect = self.throw_errors(1)
        resiliently = Resiliently(self.config)

        resiliently.call(self.callback, 'a', b='b')

        self.callback.assert_has_calls_exactly([
            call('a', b='b'),
            call('a', b='b')
        ])

    @unittest.skip("")
    def test_should_retry_specified_times(self):
        self.config.retry = 3
        self.callback.side_effect = self.throw_errors(3)
        resiliently = Resiliently(self.config)

        resiliently.call(self.callback, 'a', b='b')

        self.callback.assert_has_calls_exactly([
            call('a', b='b'),
            call('a', b='b'),
            call('a', b='b'),
            call('a', b='b')
        ])
        self.mock_sleep.assert_has_calls_exactly([
            call(1),
            call(3)
        ])

    @unittest.skip("")
    def test_should_fail_once_retry_exceeded(self):
        self.config.retry = 2
        self.callback.side_effect = self.throw_errors(3)
        resiliently = Resiliently(self.config)

        self.assertRaises(urllib2.URLError, resiliently.call, self.callback, 'a', b='b')

        self.callback.assert_has_calls_exactly([
            call('a', b='b'),
            call('a', b='b'),
            call('a', b='b')
        ])

    @unittest.skip("")
    def test_should_throttle_consecutive_calls(self):
        time_patch = patch('flickr_rsync.flickr_storage.time.time', create=True)
        mock_time = time_patch.start()
        self.config.throttling = 10
        resiliently = Resiliently(self.config)

        mock_time.return_value = 0
        resiliently.call(self.callback, 'a', b='b')
        mock_time.return_value = 1
        resiliently.call(self.callback, 'a', b='b')
        mock_time.return_value = 6
        resiliently.call(self.callback, 'a', b='b')

        self.mock_sleep.assert_has_calls_exactly([
            call(9),
            call(5)
        ])
        time_patch.stop()

    @unittest.skip("")
    def test_should_not_throttle_if_timeout_passed(self):
        time_patch = patch('flickr_rsync.flickr_storage.time.time', create=True)
        mock_time = time_patch.start()
        self.config.throttling = 10
        resiliently = Resiliently(self.config)

        mock_time.return_value = 0
        resiliently.call(self.callback, 'a', b='b')
        mock_time.return_value = 11
        resiliently.call(self.callback, 'a', b='b')

        self.mock_sleep.assert_not_called()
        time_patch.stop()

    def throw_errors(self, num):
        for x in range(num):
            yield urllib2.URLError('Bang!')
        yield True

if __name__ == '__main__':
    unittest.main(verbosity=2)

