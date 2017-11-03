from __future__ import print_function
import logging
import backoff
from throttle import throttle
from config import __packagename__

logging.getLogger('backoff').addHandler(logging.StreamHandler())
logging.getLogger('backoff').setLevel(logging.DEBUG)

_global_config = None
def get_max_tries():
    return _global_config.retry + 1
def get_delay_sec():
    return _global_config.throttling

class Resiliently(object):
    def __init__(self, config):
        global _global_config
        _global_config = config
        self._config = config

    @backoff.on_exception(backoff.expo, Exception, max_tries=get_max_tries)
    @throttle(delay_sec=get_delay_sec)
    def call(self, func, *args, **kwargs):
        return func(*args, **kwargs)
        # return self._throttle(self._retry, func, *args, **kwargs)

    def _throttle(self, func, *args, **kwargs):
        return throttle(delay_sec=self._config.throttling)(func)(*args, **kwargs)

    def _retry(self, func, *args, **kwargs):
        # We +1 this because backoff retries UP to and not including max_retries
        max_tries = self._config.retry + 1
        return backoff.on_exception(backoff.expo, Exception, max_tries=max_tries)(func)(*args, **kwargs)

