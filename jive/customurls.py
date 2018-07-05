from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtWidgets import QDialog

from jive import helper
from jive import showUrlList


class CustomUrls(QDialog, showUrlList.Ui_Dialog):
    urlList = Signal(list)

    def __init__(self, log):
        super().__init__()
        self.log = log
        self.setupUi(self)
        self.textEdit.setFocus()

        self.accepted.connect(self.ok_was_clicked)

        self.add_shortcuts()

    def ok_was_clicked(self):
        lst = self.textEdit.toPlainText().strip().splitlines()
        lst = helper.get_image_urls_only(lst)
        # print(lst)
        self.urlList.emit(lst)

    def add_shortcuts(self):
        pass
