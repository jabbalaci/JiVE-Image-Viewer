import json
import os
import shutil
from pathlib import Path

from jive import config as cfg
from jive import mylogging as log


class Settings:
    def __init__(self):
        self.d = self.read()
        self.original = self.d.copy()
        #
        if 'last_file_opened' not in self.d:
            self.d['last_file_opened'] = ""
        if 'last_dir_opened' not in self.d:
            self.d['last_dir_opened'] = ""
        if 'last_open_url_auto_detect' not in self.d:
            self.d['last_open_url_auto_detect'] = ""
        #
        self.last_file_opened = self.d['last_file_opened']
        self.last_dir_opened = self.d['last_dir_opened']
        self.last_open_url_auto_detect = self.d['last_open_url_auto_detect']

    def read(self):
        try:
            with open(cfg.SETTINGS_FILE) as f:
                d = json.load(f)
                log.info(f"{cfg.SETTINGS_FILE} was read")
                return d
        except:
            return {}    # empty dict

    def _make_dir(self):
        folder = Path(cfg.SETTINGS_FILE).parent
        if not folder.is_dir():
            folder.mkdir(parents=True)
            log.info(f"{folder} was created")

    def write(self):
        if self.d == self.original:
            # log.info(f"{cfg.SETTINGS_FILE} didn't change")
            return
        # else
        self._make_dir()
        with open(cfg.SETTINGS_FILE_BAK, "w") as f:
            json.dump(self.d, f, indent=2)
        if os.path.getsize(cfg.SETTINGS_FILE_BAK) > 0:
            shutil.move(cfg.SETTINGS_FILE_BAK, cfg.SETTINGS_FILE)
            log.info(f"{cfg.SETTINGS_FILE} was written")

    def set_last_dir_opened(self, folder):
        self.d['last_dir_opened'] = folder

    def get_last_dir_opened(self):
        return self.d['last_dir_opened']

    def set_last_file_opened(self, fname):
        self.d['last_file_opened'] = fname

    def get_last_file_opened(self):
        return self.d['last_file_opened']

    def set_last_open_url_auto_detect(self, text):
        self.d['last_open_url_auto_detect'] = text

    def get_last_open_url_auto_detect(self):
        return self.d['last_open_url_auto_detect']
