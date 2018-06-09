import logging
import os
import sys
from pathlib import Path

# BASE_DIR = str(Path(os.path.dirname(os.path.abspath(__file__))).parent)
BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
DEBUG_LOG_FILENAME = str(Path(BASE_DIR, "info.log"))

# set up formatting
formatter = logging.Formatter("%(levelname)-5s %(asctime)s %(module)s.%(funcName)s() [%(lineno)d]: %(message)s",
                              "%Y-%m-%d %H:%M:%S")

# set up logging to STDOUT for all levels DEBUG and higher
sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)

# set up logging to a file for all levels DEBUG and higher
fh = logging.FileHandler(DEBUG_LOG_FILENAME)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

# create Logger object
mylogger = logging.getLogger('MyLogger')
mylogger.setLevel(logging.DEBUG)
mylogger.addHandler(sh)    # enabled: stdout
mylogger.addHandler(fh)    # enabled: file

# create shortcut functions
debug = mylogger.debug
info = mylogger.info
warning = mylogger.warning
error = mylogger.error
critical = mylogger.critical
