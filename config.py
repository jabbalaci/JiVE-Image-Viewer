import os

if __name__ == "__main__":
    import sys
    src_dir = os.path.join(os.path.dirname(__file__), "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
# endif

from pathlib import Path
from lib.podium import get_short_fingerprint
import mylogging as log
from appdirs import AppDirs

appname = "JiveImageViewer"
app_dirs = AppDirs(appname, "")    # app_dirs.user_data_dir is what you need

DEVELOPMENT = 1
RELEASE = 2

# WHAT_IT_IS = DEVELOPMENT
WHAT_IT_IS = RELEASE

if WHAT_IT_IS == DEVELOPMENT:
    log.info("DEVELOPMENT version")
if WHAT_IT_IS == RELEASE:
    log.info("RELEASE version")

VERSION = "0.3"

HOME_DIR = os.path.expanduser("~")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = str(Path(BASE_DIR, "assets"))

SETTINGS_FILE = str(Path(app_dirs.user_data_dir, "settings.json"))
SETTINGS_FILE_BAK = str(Path(app_dirs.user_data_dir, "settings.bak"))

## BEGIN: categories.yaml
_default_categories_file = str(Path(BASE_DIR, "categories", "categories.yaml"))
CATEGORIES_FILE = _default_categories_file
machine_id = get_short_fingerprint()
if machine_id in ('91d6c2', 'b782f3'):
    CATEGORIES_FILE = str(Path(HOME_DIR, "Dropbox", "secret", "jive", "categories_full.yaml"))
if machine_id in ('dc92a4'):
    CATEGORIES_FILE = r"E:\secret\jive\categories_full.yaml"
if WHAT_IT_IS == RELEASE:
    CATEGORIES_FILE = _default_categories_file
log.info(f"using {CATEGORIES_FILE}")
## END: categories.yaml

## BEGIN: API keys
# read `api_keys.md` if you have no API keys
TUMBLR_API_KEY = os.environ.get("TUMBLR_API_KEY")

IMGUR_CLIENT_ID = os.environ.get("IMGUR_CLIENT_ID")
IMGUR_CLIENT_SECRET = os.environ.get("IMGUR_CLIENT_SECRET")
## END: API keys

ICON = str(Path(BASE_DIR, "assets", "icon.png"))
LOGO = str(Path(BASE_DIR, "assets", "logo.png"))

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

#############################################################################

if __name__ == "__main__":
    pass
