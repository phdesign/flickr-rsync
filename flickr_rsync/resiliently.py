from __future__ import print_function
import logging
import backoff
from throttle import throttle

logging.getLogger('backoff').addHandler(logging.StreamHandler())
logging.getLogger('backoff').setLevel(logging.DEBUG)

class Resiliently(object):
    def __init__(self, config):
        self._config = config
        # This is necessary to allow throttle to keep a history of calls 
        self._throttle_bind = throttle(delay_sec=self._config.throttling)

    # @backoff.on_exception(backoff.expo, Exception, max_tries=get_max_tries)
    # @throttle(delay_sec=get_delay_sec)
    def call(self, func, *args, **kwargs):
        # return func(*args, **kwargs)
        return self._throttle(self._retry, func, *args, **kwargs)

    def _throttle(self, func, *args, **kwargs):
        return self._throttle_bind(func)(*args, **kwargs)

    def _retry(self, func, *args, **kwargs):
        # We +1 this because backoff retries UP to and not including max_retries
        max_tries = self._config.retry + 1
        return backoff.on_exception(backoff.expo, Exception, max_tries=max_tries)(func)(*args, **kwargs)

