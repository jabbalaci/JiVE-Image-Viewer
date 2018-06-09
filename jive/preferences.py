import configparser
import json
import os
import sys
from pprint import pprint
from pathlib import Path


def remove_quotes(original):
    d = original.copy()
    for key, value in d.items():
        if isinstance(value, str):
            s = d[key]
            if s.startswith(('"', "'")):
                s = s[1:]
            if s.endswith(('"', "'")):
                s = s[:-1]
            d[key] = s
            # print(f"string found: {s}")
        if isinstance(value, dict):
            d[key] = remove_quotes(value)
    #
    return d


class Preferences:
    def __init__(self, preferences_ini, user_data_dir, log):
        self.preferences_ini = preferences_ini
        self.user_data_dir = user_data_dir
        self.log = log

        self.config = configparser.ConfigParser()
        if not os.path.isfile(self.preferences_ini):
            self.log.error(f"{self.preferences_ini} is missing")
            sys.exit(1)
        # else
        self.config.read(preferences_ini)

        self.d = self.to_dict(self.config._sections)

        # pprint(self.d)

        self.platform_settings = self.extract_platform_settings()
        if not self.platform_settings:
            self.log.error(f"platform specific settings were not found in {self.preferences_ini}")
            sys.exit(1)
        # else
        self.platform_settings = self.perform_string_interpolation(self.platform_settings)

    def get_platform_settings(self):
        return self.platform_settings

    def perform_string_interpolation(self, original):
        d = original.copy()

        root_dir = d['root_dir']
        if root_dir == '$DEFAULT':
            root_dir = self.user_data_dir
            d['root_dir'] = root_dir

        for key, value in d.items():
            if value.startswith("$root_dir"):
                d[key] = value.replace("$root_dir", root_dir)

        return d

    def to_dict(self, config):
        """
        Nested OrderedDict to normal dict.
        Also, remove the annoying quotes (apostrophes) from around string values.
        """
        d = json.loads(json.dumps(config))
        d = remove_quotes(d)
        return d

    def extract_platform_settings(self):
        text = sys.platform
        try:
            if text.startswith("linux"):
                return self.d["Linux"]
            if text.startswith("win"):
                return self.d["Windows"]
            return {}                       # TODO : extend the code here if you have a Mac
        except KeyError:
            self.log.error(f"missing section in {self.preferences_ini}: [{text.capitalize()}]")
            return {}

    def make_directories(self, d):
        """
        Gets a directory list and creates all of them if they don't exist.
        Exit with an error in case of problem.
        """
        directory_keys = ('root_dir', 'saves_dir', 'wallpapers_dir', 'tmp_dir', 'cache_dir')

        for key in directory_keys:
            entry = d[key]
            p = Path(entry)
            if not p.is_dir():
                try:
                    p.mkdir(parents=True)
                    self.log.info(f"create folder: {entry}")
                except:
                    self.log.error(f"couldn't create the folder {entry}")
                    sys.exit(1)
            #
        #