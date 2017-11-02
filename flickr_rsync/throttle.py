from __future__ import print_function
import time
from functools import wraps
from verbose import vprint

def _maybe_call(f, *args, **kwargs):
    return f(*args, **kwargs) if callable(f) else f

_last_call = None
def throttle(delay_sec=0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global _last_call
            delay_sec_ = _maybe_call(delay_sec)
            if delay_sec_ > 0 and _last_call != None:
                delay = delay_sec_ - (time.time() - _last_call)
                if delay > 0:
                    vprint('Throttle: sleeping for {} seconds'.format(delay))
                    time.sleep(delay)
            _last_call = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

