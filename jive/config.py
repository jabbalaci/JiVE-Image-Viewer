if __name__ == "__main__":
    import os, sys
    # This is a trick. This way I can launch
    # this file during the development.
    folder = os.path.join(os.path.dirname(__file__), "..")
    if folder not in sys.path:
        sys.path.insert(0, folder)
    sys.argv[0] = "../start.py"
# endif

#############################################################################

import sys

import os
from appdirs import AppDirs
from pathlib import Path
from pprint import pprint

from jive import mylogging as log
from jive import preferences

VERSION = "0.5"

appname = "JiveImageViewer"
app_dirs = AppDirs(appname, "")    # app_dirs.user_data_dir is what we need

HOME_DIR = os.path.expanduser("~")
BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
ASSETS_DIR = str(Path(BASE_DIR, "assets"))

SETTINGS_FILE = str(Path(app_dirs.user_data_dir, "settings.json"))
SETTINGS_FILE_BAK = str(Path(app_dirs.user_data_dir, "settings.bak"))

PREFERENCES_INI = str(Path(BASE_DIR, "preferences.ini"))

categories_file_default = Path(BASE_DIR, "categories", "categories.yaml")
categories_file_personal = Path(app_dirs.user_data_dir, "categories.yaml")

def categories_file():
    if categories_file_personal.is_file():
        return str(categories_file_personal)
    # else
    return str(categories_file_default)

## BEGIN: API keys
# read `api_keys.md` if you have no API keys
TUMBLR_API_KEY = os.environ.get("TUMBLR_API_KEY")

IMGUR_CLIENT_ID = os.environ.get("IMGUR_CLIENT_ID")
IMGUR_CLIENT_SECRET = os.environ.get("IMGUR_CLIENT_SECRET")
## END: API keys

ICON = str(Path(ASSETS_DIR, "icon.png"))
LOGO = str(Path(ASSETS_DIR, "logo.png"))

LONG = 1024    # for labels' widths to avoid text truncation

# for ex. 80 means that the image's width must be 80% of the window's width
IMG_WIDTH_TO_WINDOW_WIDTH_IN_PERCENT = 80

# all possible formats:
# SUPPORTED_FORMATS = { ".bmp", ".gif", ".jpg", ".jpe", ".jpeg", ".png", ".pbm", ".pgm", ".ppm", ".xbm", ".xpm" }
# without .gif:
SUPPORTED_FORMATS = { ".bmp", ".jpg", ".jpe", ".jpeg", ".png", ".pbm", ".pgm", ".ppm", ".xbm", ".xpm" }

MESSAGE_FLASH_TIME_1 = 1000    # in msec.
MESSAGE_FLASH_TIME_2 = 2000    # in msec.
MESSAGE_FLASH_TIME_3 = 3000    # in msec.

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
}

SEPARATOR = "-----"

TOP_AND_BOTTOM_BAR_STYLESHEET = "background: lightgray"

prefs = preferences.Preferences(PREFERENCES_INI, app_dirs.user_data_dir, log)
PLATFORM_SETTINGS = prefs.get_platform_settings()
prefs.make_directories(PLATFORM_SETTINGS)
PREFERENCES_OPTIONS = prefs.get_as_dict().get('Options')

NORMAL_SAVE = 1
WALLPAPER_SAVE = 2

REQUESTS_TIMEOUT = 3    # seconds

#############################################################################

if __name__ == "__main__":
    pprint(PLATFORM_SETTINGS)
    # pass
