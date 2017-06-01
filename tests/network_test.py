# -*- coding: utf-8 -*-
import os, sys
import unittest
import urllib2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libs')
from mock import MagicMock, patch, call
import helpers
from flickr_rsync.flickr_storage import Network

class NetworkTest(unittest.TestCase):

    def setUp(self):
        self.print_patch = patch('flickr_rsync.flickr_storage.print', create=True)
        self.mock_print = self.print_patch.start()
        self.sleep_patch = patch('flickr_rsync.flickr_storage.time.sleep', create=True)
        self.mock_sleep = self.sleep_patch.start()

        self.config = MagicMock()
        self.callback = MagicMock()

    def tearDown(self):
        self.print_patch.stop()
        self.sleep_patch.stop()

    def test_should_make_remote_call(self):
        network = Network(self.config)

        network.call(self.callback, 'a', b='b')

        self.callback.assert_called_once_with('a', b='b')

    def test_should_retry_once_with_backoff(self):
        self.config.retry = 1
        self.callback.side_effect = self.throw_errors(1)
        network = Network(self.config)

        network.call(self.callback, 'a', b='b')

        self.callback.assert_has_calls_exactly([
            call('a', b='b'),
            call('a', b='b')
        ])

    def test_should_retry_specified_times(self):
        self.config.retry = 3
        self.callback.side_effect = self.throw_errors(3)
        network = Network(self.config)

        network.call(self.callback, 'a', b='b')

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

    def test_should_fail_once_retry_exceeded(self):
        self.config.retry = 2
        self.callback.side_effect = self.throw_errors(3)
        network = Network(self.config)

        self.assertRaises(urllib2.URLError, network.call, self.callback, 'a', b='b')

        self.callback.assert_has_calls_exactly([
            call('a', b='b'),
            call('a', b='b'),
            call('a', b='b')
        ])

    def test_should_throttle_consecutive_calls(self):
        time_patch = patch('flickr_rsync.flickr_storage.time.time', create=True)
        mock_time = time_patch.start()
        self.config.throttling = 10
        network = Network(self.config)

        mock_time.return_value = 0
        network.call(self.callback, 'a', b='b')
        mock_time.return_value = 1
        network.call(self.callback, 'a', b='b')
        mock_time.return_value = 6
        network.call(self.callback, 'a', b='b')

        self.mock_sleep.assert_has_calls_exactly([
            call(9),
            call(5)
        ])
        time_patch.stop()

    def test_should_not_throttle_if_timeout_passed(self):
        time_patch = patch('flickr_rsync.flickr_storage.time.time', create=True)
        mock_time = time_patch.start()
        self.config.throttling = 10
        network = Network(self.config)

        mock_time.return_value = 0
        network.call(self.callback, 'a', b='b')
        mock_time.return_value = 11
        network.call(self.callback, 'a', b='b')

        self.mock_sleep.assert_not_called()
        time_patch.stop()

    def throw_errors(self, num):
        for x in range(num):
            yield urllib2.URLError('Bang!')
        yield True

if __name__ == '__main__':
    unittest.main(verbosity=2)

