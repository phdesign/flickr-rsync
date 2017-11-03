from __future__ import print_function
import logging
import backoff
from throttle import throttle
from config import __packagename__

logging.getLogger('backoff').addHandler(logging.StreamHandler())
logging.getLogger('backoff').setLevel(logging.DEBUG)

class Resiliently(object):
    def __init__(self, config):
        self._config = config

    def call(self, func, *args, **kwargs):
        return self._throttle(self._retry, func, *args, **kwargs)

    def _throttle(self, func, *args, **kwargs):
        return throttle(delay_sec=self._config.throttling)(func)(*args, **kwargs)

    def _retry(self, func, *args, **kwargs):
        # We +1 this because backoff retries UP to and not including max_retries
        max_tries = self._config.retry + 1
        return backoff.on_exception(backoff.expo, Exception, max_tries=max_tries)(func)(*args, **kwargs)

