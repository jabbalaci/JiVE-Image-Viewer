"""
Open a file with an external application.
"""

import sys

from PyQt5.QtWidgets import (QMessageBox)
from subprocess import Popen

from jive import config as cfg
from jive.exceptions import MissingPreferencesEntry


def open_folder(dname):
    text = sys.platform
    if text.startswith("linux"):
        Popen(["xdg-open", dname])
    if text.startswith("win"):
        Popen(["explorer", dname])
    if text.startswith("darwin"):
        Popen(["open", dname])  # TODO : somebody try it on Mac!


def open_file_with_editor(parent, fname):
    editor = cfg.PLATFORM_SETTINGS.get('editor')
    try:
        if editor:
            Popen([editor, fname])
        else:
            raise MissingPreferencesEntry
    except MissingPreferencesEntry:
        msg = f"You should provide a text editor in {cfg.PREFERENCES_INI}"
        QMessageBox.warning(parent, "Warning", msg)
    except:
        msg = f"""The file can't be opened with {editor}.

Please verify your text editor in {cfg.PREFERENCES_INI}
""".strip()
        QMessageBox.critical(parent, "Error", msg)


def open_file_with_gimp(parent, fname):
    gimp = cfg.PLATFORM_SETTINGS.get('gimp')
    try:
        if gimp:
            Popen([gimp, fname])
        else:
            raise MissingPreferencesEntry
    except MissingPreferencesEntry:
        msg = f"You should provide Gimp in {cfg.PREFERENCES_INI}"
        QMessageBox.warning(parent, "Warning", msg)
    except:
        msg = f"""The file can't be opened with {gimp}.

Please verify your Gimp entry in {cfg.PREFERENCES_INI}
""".strip()
        QMessageBox.critical(parent, "Error", msg)