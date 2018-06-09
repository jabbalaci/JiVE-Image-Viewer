from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget, QProgressBar

from jive import config as cfg


class StatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        #
        self.message_label = QLabel(self)
        self.sep1 = QLabel("|", self)
        self.curr_pos_label = QLabel(self)
        self.sep2 = QLabel("|", self)
        self.file_name_label = QLabel(self)
        self.sep3 = QLabel("|", self)
        self.resolution_label = QLabel(self)
        self.sep4 = QLabel("|", self)
        # self.memory_label = QLabel(self)
        # self.sep5 = QLabel("|", self)
        self.mode_label = QLabel(self)
        self.sep5 = QLabel("|", self)
        self.progressbar = QProgressBar(self)
        self.progressbar.setMaximumWidth(150)
        self.progressbar.setMaximumHeight(15)
        self.progressbar.hide()
        #
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.layout().addWidget(self.message_label)
        self.layout().addWidget(self.sep1)
        self.layout().addWidget(self.curr_pos_label)
        self.layout().addWidget(self.sep2)
        self.layout().addWidget(self.resolution_label)
        self.layout().addWidget(self.sep3)
        self.layout().addWidget(self.file_name_label)
        self.layout().addWidget(self.sep4)
        # self.layout().addWidget(self.memory_label)
        # self.layout().addWidget(self.sep5)
        self.layout().addWidget(self.mode_label)
        self.layout().addWidget(self.sep5)
        self.layout().addWidget(self.progressbar)
        #
        self.message_timer = None

    def reset(self):
        self.message_label.setText("")
        self.curr_pos_label.setText("")
        self.file_name_label.setText("")
        self.resolution_label.setText("")

    def flash_message(self, msg, wait=cfg.MESSAGE_FLASH_TIME_2):
        self.message_label.setText(msg)
        if self.message_timer:
            self.message_timer.stop()
            self.message_timer.deleteLater()
        self.message_timer = QTimer()
        self.message_timer.timeout.connect(self.delete_flashed_message)
        self.message_timer.setSingleShot(True)
        self.message_timer.start(wait)

    def delete_flashed_message(self):
        self.message_label.setText("")