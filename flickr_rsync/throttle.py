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
from functools import wraps
from verbose import vprint

def _maybe_call(f, *args, **kwargs):
    return f(*args, **kwargs) if callable(f) else f

def throttle(delay_sec=0):
    print('Init decorator')
    class state:
        last_call = None
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay_sec_ = _maybe_call(delay_sec)
            print('_last_call: {}'.format(state.last_call))
            if delay_sec_ > 0 and state.last_call != None:
                delay = delay_sec_ - (time.time() - state.last_call)
                if delay > 0:
                    vprint('Throttle: sleeping for {} seconds'.format(delay))
                    time.sleep(delay)
            state.last_call = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

