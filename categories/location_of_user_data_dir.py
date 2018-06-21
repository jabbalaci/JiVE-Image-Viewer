#!/usr/bin/env python3

"""
The app. creates a settings.json file.
This little tool shows you the location of that file.
"""

if __name__ == "__main__":
    import os, sys
    folder = os.path.join(os.path.dirname(__file__), "..")
    if folder not in sys.path:
        sys.path.insert(0, folder)
    sys.argv[0] = "../start.py"
# endif


from jive import config as cfg


print()
print("Your user data dir. is located here: {0}".format(cfg.app_dirs.user_data_dir))
