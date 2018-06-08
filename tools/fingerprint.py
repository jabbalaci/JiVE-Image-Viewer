#!/usr/bin/env python3

"""
Print the short fingerprint of your machine.

It can be used in `config.py` to customize some
settings to a given machine.
"""

if __name__ == "__main__":
    import os
    import sys
    folder = os.path.join(os.path.dirname(__file__), "..")
    if folder not in sys.path:
        sys.path.insert(0, folder)
# endif

from jive.lib.podium import get_short_fingerprint

print("short fingerprint of this machine: {0}".format(get_short_fingerprint()))
