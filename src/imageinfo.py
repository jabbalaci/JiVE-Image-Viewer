from functools import partial
from pathlib import Path

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QDialog, QShortcut, QGroupBox, QGridLayout, QLabel, QVBoxLayout, QPushButton, QApplication

import config as cfg
import helper
from helper import bold

ICON_SIZE = 16


class ImageInfo(QDialog):
    def __init__(self, parent, img):
        super().__init__()
        self.parent = parent
        self.img = img

        self.setModal(True)    # not sure if it should be modal or not
        # self.parent.setEnabled(False)
        self.setWindowTitle("Image info")
        self.setWindowIcon(QtGui.QIcon(str(Path(cfg.ASSETS_DIR, "info.png"))))

        self.add_shortcuts()
        self.grid_layout_creation()

        vbox = QVBoxLayout()
        vbox.addWidget(self.group_box)
        self.setLayout(vbox)

        self.show()

    # def closeEvent(self, event):
    #     self.parent.setEnabled(True)

    def grid_layout_creation(self):
        self.group_box = QGroupBox("Info")

        layout = QGridLayout()
        layout.addWidget(QLabel(bold("Local file?")), 0, 0)
        layout.addWidget(QLabel("Yes" if self.img.local_file else "No"), 0, 1)

        layout.addWidget(QLabel(bold("Path:")), 1, 0)
        text = self.img.get_absolute_path_or_url()
        layout.addWidget(QLabel(text), 1, 1)
        icon = QtGui.QIcon(str(Path(cfg.ASSETS_DIR, "clipboard.png")))
        btn = QPushButton()
        btn.setIcon(icon)
        btn.setIconSize(QtCore.QSize(ICON_SIZE, ICON_SIZE))
        btn.setToolTip("copy to clipboard")
        btn.clicked.connect(partial(self.copy_to_clipboard, text))
        layout.addWidget(btn, 1, 2)

        layout.addWidget(QLabel(bold("Resolution:")), 2, 0)
        text = "{w} x {h} pixels".format(w=self.img.original_img.width(), h=self.img.original_img.height())
        layout.addWidget(QLabel(text), 2, 1)

        layout.addWidget(QLabel(bold("Size:")), 3, 0)
        file_size_hr = self.img.get_file_size(human_readable=True)
        text = "{0} ({1} bytes)".format(file_size_hr, helper.pretty_num(self.img.get_file_size()))
        layout.addWidget(QLabel(text), 3, 1)

        layout.addWidget(QLabel(bold("Flags:")), 4, 0)
        text = self.img.get_flags()
        layout.addWidget(QLabel(text), 4, 1)

        self.group_box.setLayout(layout)

    def copy_to_clipboard(self, text):
        cb = QApplication.clipboard()
        cb.setText(text)

    def add_shortcuts(self):
        self.shortcutCloseI = QShortcut(QKeySequence("I"), self)
        self.shortcutCloseI.activated.connect(self.close)

        self.shortcutCloseQ = QShortcut(QKeySequence("Q"), self)
        self.shortcutCloseQ.activated.connect(self.close)