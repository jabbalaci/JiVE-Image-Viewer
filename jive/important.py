"""
Information about the important files and folders.
"""

from PyQt5 import QtGui
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox,
                             QLabel, QPushButton, QShortcut, QVBoxLayout)
from functools import partial
from pathlib import Path

from jive import config as cfg
from jive import opener
from jive.helper import bold

ICON_SIZE = 16


class ImportantFilesAndFolders(QDialog):
    def __init__(self, parent) -> None:
        super().__init__()
        self.parent = parent

        self.setWindowTitle("Important files and folders")
        self.setWindowIcon(QtGui.QIcon(str(Path(cfg.ASSETS_DIR, "info.png"))))

        self.add_shortcuts()
        self.grid_layout_creation_1()
        self.grid_layout_creation_2()

        vbox = QVBoxLayout()
        vbox.addWidget(self.group_box_1)
        vbox.addWidget(self.group_box_2)
        self.setLayout(vbox)

        self.btn_saves.setFocus()

        self.show()

    def grid_layout_creation_1(self) -> None:
        self.group_box_1 = QGroupBox("Files")
        row = -1

        d = cfg.PLATFORM_SETTINGS

        # pprint(d)

        layout = QGridLayout()
        row += 1
        layout.addWidget(QLabel(bold("preferences.ini:")), row, 0)
        fname = cfg.PREFERENCES_INI
        layout.addWidget(QLabel(fname), row, 1)
        btn = QPushButton("Open")
        btn.clicked.connect(partial(opener.open_file_with_editor, self, fname))
        layout.addWidget(btn, row, 2)

        row += 1
        layout.addWidget(QLabel(bold("categories.yaml:")), row, 0)
        fname = cfg.categories_file()
        layout.addWidget(QLabel(fname), row, 1)
        btn = QPushButton("Open")
        btn.clicked.connect(partial(opener.open_file_with_editor, self, fname))
        layout.addWidget(btn, row, 2)

        row += 1
        layout.addWidget(QLabel(bold("settings.json:")), row, 0)
        fname = cfg.SETTINGS_FILE
        layout.addWidget(QLabel(fname), row, 1)
        btn = QPushButton("Open")
        btn.clicked.connect(partial(opener.open_file_with_editor, self, fname))
        layout.addWidget(btn, row, 2)

        self.group_box_1.setLayout(layout)

    def grid_layout_creation_2(self) -> None:
        self.group_box_2 = QGroupBox("Folders")
        row = -1

        d = cfg.PLATFORM_SETTINGS

        layout = QGridLayout()
        row += 1
        layout.addWidget(QLabel(bold("application folder:")), row, 0)
        dname = cfg.BASE_DIR
        layout.addWidget(QLabel(dname), row, 1)
        btn = QPushButton("Open")
        btn.clicked.connect(partial(opener.open_folder, dname))
        layout.addWidget(btn, row, 2)

        row += 1
        layout.addWidget(QLabel(bold("user data dir.:")), row, 0)
        dname = d['root_dir']
        layout.addWidget(QLabel(dname), row, 1)
        btn = QPushButton("Open")
        btn.clicked.connect(partial(opener.open_folder, dname))
        layout.addWidget(btn, row, 2)

        row += 1
        layout.addWidget(QLabel(bold("saves dir.:")), row, 0)
        dname = d['saves_dir']
        layout.addWidget(QLabel(dname), row, 1)
        self.btn_saves = QPushButton("Open")
        self.btn_saves.clicked.connect(partial(opener.open_folder, dname))
        layout.addWidget(self.btn_saves, row, 2)

        row += 1
        layout.addWidget(QLabel(bold("wallpapers dir.:")), row, 0)
        dname = d['wallpapers_dir']
        layout.addWidget(QLabel(dname), row, 1)
        btn = QPushButton("Open")
        btn.clicked.connect(partial(opener.open_folder, dname))
        layout.addWidget(btn, row, 2)

        row += 1
        layout.addWidget(QLabel(bold("tmp dir.:")), row, 0)
        dname = d['tmp_dir']
        layout.addWidget(QLabel(dname), row, 1)
        btn = QPushButton("Open")
        btn.clicked.connect(partial(opener.open_folder, dname))
        layout.addWidget(btn, row, 2)

        row += 1
        layout.addWidget(QLabel(bold("cache dir.:")), row, 0)
        dname = d['cache_dir']
        layout.addWidget(QLabel(dname), row, 1)
        btn = QPushButton("Open")
        btn.clicked.connect(partial(opener.open_folder, dname))
        layout.addWidget(btn, row, 2)

        self.group_box_2.setLayout(layout)

    def copy_to_clipboard(self, text: str) -> None:
        cb = QApplication.clipboard()
        cb.setText(text)

    def add_shortcuts(self) -> None:
        self.shortcutCloseQ = QShortcut(QKeySequence("Q"), self)
        self.shortcutCloseQ.activated.connect(self.close)
