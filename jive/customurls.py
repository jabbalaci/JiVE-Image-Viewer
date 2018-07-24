import os
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtWidgets import QDialog, QFileDialog

from jive import helper
from jive import showUrlList


class CustomUrls(QDialog, showUrlList.Ui_Dialog):
    urlList = Signal(list)

    def __init__(self, log) -> None:
        super().__init__()
        self.log = log
        self.setupUi(self)
        self.textEdit.setFocus()

        self.accepted.connect(self.ok_was_clicked)
        self.readFromFileButton.clicked.connect(self.read_from_file)

        self.clearButton.clicked.connect(self.clear_list)

        self.toClipboardButton.clicked.connect(self.copy_list_to_clipboard)

        self.fromClipboardButton.clicked.connect(self.paste_list_from_clipboard)

        self.add_shortcuts()

    def paste_list_from_clipboard(self) -> None:
        text = helper.get_text_from_clipboard()
        self.textEdit.clear()
        self.textEdit.appendPlainText(text)

    def copy_list_to_clipboard(self) -> None:
        content = self.textEdit.toPlainText().strip() + "\n"
        helper.copy_text_to_clipboard(content)

    def clear_list(self) -> None:
        self.textEdit.clear()
        self.textEdit.setFocus()

    def read_from_file(self) -> None:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filter = "Text files (*.txt)"
        file_obj = QFileDialog.getOpenFileName(self,
                                               caption="Open Text File",
                                               # directory=str(Path(self.settings.get_last_file_opened()).parent),
                                               filter=filter,
                                               initialFilter=filter,
                                               options=options)
        fname = file_obj[0]
        if os.path.isfile(fname):
            with open(fname) as f:
                lines = f.read().splitlines()

            cnt = len(lines)
            for line in lines:
                line = line.rstrip("\n")
                self.textEdit.appendPlainText(line)
            for _ in range(cnt):
                self.textEdit.moveCursor(QtGui.QTextCursor.Up, QtGui.QTextCursor.MoveAnchor)  # go back to top

    def ok_was_clicked(self) -> None:
        lst = self.textEdit.toPlainText().strip().splitlines()
        lst = helper.get_image_urls_only(lst)
        # print(lst)
        self.urlList.emit(lst)

    def add_shortcuts(self) -> None:
        pass
