if __name__ == "__main__":
    import os, sys
    # This is a trick. This way I can launch
    # this file during the development.
    folder: str = os.path.join(os.path.dirname(__file__), "..")
    if folder not in sys.path:
        sys.path.insert(0, folder)
    sys.argv[0] = "../start.py"
# endif

#############################################################################

import os
from appdirs import AppDirs
from pathlib import Path
from typing import Set, Dict, Optional

from jive import mylogging as log
from jive.preferences import Preferences

VERSION: str = "0.7.1"

appname: str = "JiveImageViewer"
app_dirs: AppDirs = AppDirs(appname, "")    # app_dirs.user_data_dir is what we need

HOME_DIR: str = os.path.expanduser("~")
# BASE_DIR: str = os.path.dirname(os.path.abspath(sys.argv[0]))    # use this when creating EXE !!!
BASE_DIR: str = str(Path(os.path.dirname(os.path.abspath(__file__))).parent)    # we need this for running tests
ASSETS_DIR: str = str(Path(BASE_DIR, "assets"))

SETTINGS_FILE: str = str(Path(app_dirs.user_data_dir, "settings.json"))
SETTINGS_FILE_BAK: str = str(Path(app_dirs.user_data_dir, "settings.bak"))

PREFERENCES_INI: str = str(Path(BASE_DIR, "preferences.ini"))

ERROR_SOUND: str = str(Path(ASSETS_DIR, "error.wav"))

categories_file_default: Path = Path(BASE_DIR, "categories", "categories.yaml")
categories_file_personal: Path = Path(app_dirs.user_data_dir, "categories.yaml")

def categories_file():
    if categories_file_personal.is_file():
        return str(categories_file_personal)
    # else
    return str(categories_file_default)

## BEGIN: API keys
# read `api_keys.md` if you have no API keys
TUMBLR_API_KEY: Optional[str] = os.environ.get("TUMBLR_API_KEY")

IMGUR_CLIENT_ID: Optional[str] = os.environ.get("IMGUR_CLIENT_ID")
IMGUR_CLIENT_SECRET: Optional[str] = os.environ.get("IMGUR_CLIENT_SECRET")
## END: API keys

ICON: str = str(Path(ASSETS_DIR, "icon.png"))
LOGO: str = str(Path(ASSETS_DIR, "logo.png"))
LOADING: str = str(Path(ASSETS_DIR, "loading.png"))

LONG: int = 1024    # for labels' widths to avoid text truncation

# for ex. 80 means that the image's width must be 80% of the window's width
IMG_WIDTH_TO_WINDOW_WIDTH_IN_PERCENT: int = 80

# all possible formats:
# SUPPORTED_FORMATS = { ".bmp", ".gif", ".jpg", ".jpe", ".jpeg", ".png", ".pbm", ".pgm", ".ppm", ".xbm", ".xpm" }
# without .gif:
SUPPORTED_FORMATS: Set[str] = { ".bmp", ".jpg", ".jpe", ".jpeg", ".png", ".pbm", ".pgm", ".ppm", ".xbm", ".xpm" }

MESSAGE_FLASH_TIME_1: int = 1000    # in msec.
MESSAGE_FLASH_TIME_2: int = 2000    # in msec.
MESSAGE_FLASH_TIME_3: int = 3000    # in msec.

headers: Dict[str, str] = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
}

SEPARATOR: str = "-----"

TOP_AND_BOTTOM_BAR_STYLESHEET: str = "background: lightgray"

prefs: Preferences = Preferences(PREFERENCES_INI, app_dirs.user_data_dir, log)
PLATFORM_SETTINGS: Dict[str, str] = prefs.get_platform_settings()
prefs.make_directories(PLATFORM_SETTINGS)
PREFERENCES_OPTIONS: Dict[str, str] = prefs.get_as_dict().get('Options')

NORMAL_SAVE: int = 1
WALLPAPER_SAVE: int = 2

REQUESTS_TIMEOUT: int = 3    # seconds

#############################################################################

if __name__ == "__main__":
    # pprint(PLATFORM_SETTINGS)
    # print(AutoDetect.sequence_url.value)
    # print(PREFERENCES_OPTIONS)
    pass