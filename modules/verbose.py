from __future__ import print_function

_config = None
def set_config(config):
    global _config
    _config = config

def vprint(*args, **kwargs):
    if _config.verbose:
        print(*args, **kwargs)
