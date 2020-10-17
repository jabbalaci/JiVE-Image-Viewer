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
from typing import Dict, Optional

from jive import mylogging as log
from jive.preferences import Preferences

VERSION = "0.7.5"
tmp = sys.version    # Leave it here! This way "import sys" won't be removed accidentally.

appname = "JiveImageViewer"
app_dirs = AppDirs(appname, "")    # app_dirs.user_data_dir is what we need

HOME_DIR = os.path.expanduser("~")
# BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))    # use this when creating EXE !!!
BASE_DIR = str(Path(os.path.dirname(os.path.abspath(__file__))).parent)    # we need this for running tests
ASSETS_DIR = str(Path(BASE_DIR, "assets"))

SETTINGS_FILE = str(Path(app_dirs.user_data_dir, "settings.json"))
SETTINGS_FILE_BAK = str(Path(app_dirs.user_data_dir, "settings.bak"))

PREFERENCES_INI = str(Path(BASE_DIR, "preferences.ini"))

ERROR_SOUND = str(Path(ASSETS_DIR, "error.wav"))

# BEGIN: categories
categories_file_default = Path(BASE_DIR, "categories", "categories.yaml")
categories_file_personal = Path(app_dirs.user_data_dir, "categories.yaml")

def categories_file() -> str:
    if categories_file_personal.is_file():
        return str(categories_file_personal)
    # else
    return str(categories_file_default)
# END: categories

# BEGIN: bookmarks
bookmarks_file_default = Path(BASE_DIR, "bookmarks", "bookmarks.yaml")
bookmarks_file_personal = Path(app_dirs.user_data_dir, "bookmarks.yaml")

def bookmarks_file() -> str:
    if bookmarks_file_personal.is_file():
        return str(bookmarks_file_personal)
    # else
    return str(bookmarks_file_default)
# END: bookmarks

## BEGIN: API keys
# read `api_keys.md` if you have no API keys
TUMBLR_API_KEY: Optional[str] = os.environ.get("TUMBLR_API_KEY")

IMGUR_CLIENT_ID: Optional[str] = os.environ.get("IMGUR_CLIENT_ID")
IMGUR_CLIENT_SECRET: Optional[str] = os.environ.get("IMGUR_CLIENT_SECRET")
## END: API keys

ICON = str(Path(ASSETS_DIR, "icon.png"))
LOGO = str(Path(ASSETS_DIR, "logo.png"))
LOADING = str(Path(ASSETS_DIR, "loading.png"))

LONG = 1024    # for labels' widths to avoid text truncation

# for ex. 80 means that the image's width must be 80% of the window's width
IMG_WIDTH_TO_WINDOW_WIDTH_IN_PERCENT = 80

# all possible formats:
# SUPPORTED_FORMATS = { ".bmp", ".gif", ".jpg", ".jpe", ".jpeg", ".png", ".pbm", ".pgm", ".ppm", ".xbm", ".xpm" }
# without .gif:
SUPPORTED_FORMATS = { ".bmp", ".jpg", ".jpe", ".jpeg", ".png", ".pbm", ".pgm", ".ppm", ".xbm", ".xpm" }

MESSAGE_FLASH_TIME_1 = 1 * 1000    # in msec.
MESSAGE_FLASH_TIME_2 = 2 * 1000    # in msec.
MESSAGE_FLASH_TIME_3 = 3 * 1000    # in msec.
MESSAGE_FLASH_TIME_4 = 4 * 1000    # in msec.
MESSAGE_FLASH_TIME_5 = 5 * 1000    # in msec.
MESSAGE_FLASH_TIME_6 = 6 * 1000    # in msec.
MESSAGE_FLASH_TIME_7 = 7 * 1000    # in msec.
MESSAGE_FLASH_TIME_8 = 8 * 1000    # in msec.

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0',
}

SEPARATOR = "-----"

TOP_AND_BOTTOM_BAR_STYLESHEET = "background: lightgray"

prefs = Preferences(PREFERENCES_INI, app_dirs.user_data_dir, log)
PLATFORM_SETTINGS: Dict[str, str] = prefs.get_platform_settings()
prefs.make_directories(PLATFORM_SETTINGS)
PREFERENCES_OPTIONS: Dict[str, str] = prefs.get_as_dict().get('Options', {})

NORMAL_SAVE = 1
WALLPAPER_SAVE = 2

REQUESTS_TIMEOUT = 5    # seconds

#############################################################################

if __name__ == "__main__":
    # pprint(PLATFORM_SETTINGS)
    # print(AutoDetect.sequence_url.value)
    # print(PREFERENCES_OPTIONS)
    pass
