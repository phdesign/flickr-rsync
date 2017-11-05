# ------------------------------------
# Name: throttle
# Description:
#   Decorator to throttle calls to a function. Will only allow a function to be called once every 'delay_sec' seconds.
# Params:
#   - delay_sec: Minimum number of seconds between subsequent calls to the decorated function. May be a decimal number.
# Example:
#   @throttle(delay_sec=0.5)
#   def my_function():
# ------------------------------------

from __future__ import print_function
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# Copied from 'backoff' project
def _maybe_call(f, *args, **kwargs):
    return f(*args, **kwargs) if callable(f) else f

class HistoryItem(object):
    def __init__(self, func):
        self.func = func
        self.last_call = None

history = []
def throttle(delay_sec=0):
    def decorator(func):
        state = next((x for x in history if x.func == func), None)
        if state == None:
            state = HistoryItem(func)
            history.append(state)
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay_sec_ = _maybe_call(delay_sec)
            if delay_sec_ > 0 and state.last_call != None:
                delay = delay_sec_ - (time.time() - state.last_call)
                if delay > 0:
                    logger.debug('throttling function call, sleeping for {} seconds'.format(delay))
                    time.sleep(delay)
            state.last_call = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

