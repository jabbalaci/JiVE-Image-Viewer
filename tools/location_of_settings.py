#!/usr/bin/env python3

"""
The app. creates a settings.json file.
This little tool shows you the location of that file.
"""

import os

if __name__ == "__main__":
    import sys
    folder = os.path.join(os.path.dirname(__file__), "..")
    if folder not in sys.path:
        sys.path.insert(0, folder)
    folder = os.path.join(os.path.dirname(__file__), "../src")
    if folder not in sys.path:
        sys.path.insert(0, folder)
# endif

import config as cfg

print()
print("Your settings file is located here: {0}".format(cfg.SETTINGS_FILE))
