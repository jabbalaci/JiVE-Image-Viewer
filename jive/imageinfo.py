from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox,
                             QLabel, QPushButton, QShortcut, QVBoxLayout)
from functools import partial
from pathlib import Path

from jive import config as cfg
from jive import helper
from jive.helper import bold

ICON_SIZE = 16


class ImageInfo(QDialog):
    def __init__(self, parent, img) -> None:
        super().__init__()
        self.parent = parent
        self.commit = self.parent.commit
        self.img = img

        self.setModal(True)    # not sure if it should be modal or not
        # self.parent.setEnabled(False)
        self.setWindowTitle("Image info")
        self.setWindowIcon(QtGui.QIcon(str(Path(cfg.ASSETS_DIR, "info.png"))))

        self.add_shortcuts()
        self.grid_layout_creation_1()
        self.grid_layout_creation_2()

        vbox = QVBoxLayout()
        vbox.addWidget(self.group_box_1)
        vbox.addWidget(self.group_box_2)
        self.setLayout(vbox)

        self.show()

    # def closeEvent(self, event):
    #     self.parent.setEnabled(True)

    def grid_layout_creation_1(self) -> None:
        self.group_box_1 = QGroupBox("Image info")

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

        self.group_box_1.setLayout(layout)

    def grid_layout_creation_2(self) -> None:
        self.group_box_2 = QGroupBox("Summary")

        length = len(self.parent.imgList.get_list_of_images())

        layout = QGridLayout()
        layout.addWidget(QLabel(bold("Marked to be saved:")), 0, 0)
        num = self.commit.to_save()
        text = f"{num} (out of {length})"
        layout.addWidget(QLabel(text), 0, 1)

        layout.addWidget(QLabel(bold("Marked to be deleted:")), 1, 0)
        num = self.commit.to_delete()
        remain = len(self.parent.imgList.get_list_of_images()) - num
        text = f"{num} (out of {length}) [remain {remain}]"
        layout.addWidget(QLabel(text), 1, 1)

        layout.addWidget(QLabel(bold("Marked to save as wallpaper:")), 2, 0)
        num = self.commit.to_wallpaper()
        text = f"{num} (out of {length})"
        layout.addWidget(QLabel(text), 2, 1)

        self.group_box_2.setLayout(layout)

    def copy_to_clipboard(self, text: str) -> None:
        cb = QApplication.clipboard()
        cb.setText(text)

    def add_shortcuts(self) -> None:
        self.shortcutCloseI = QShortcut(QKeySequence("I"), self)
        self.shortcutCloseI.activated.connect(self.close)

        self.shortcutCloseQ = QShortcut(QKeySequence("Q"), self)
        self.shortcutCloseQ.activated.connect(self.close)
