#!/usr/bin/env python3

"""
Print the short fingerprint of your machine.

It can be used in `config.py` to customize some
settings to a given machine.
"""

import os

if __name__ == "__main__":
    import sys
    src_dir = os.path.join(os.path.dirname(__file__), "../src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
# endif

from lib.podium import get_short_fingerprint

print("short fingerprint of this machine: {0}".format(get_short_fingerprint()))
