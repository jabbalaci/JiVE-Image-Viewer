#!/usr/bin/env python3

from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtWidgets import QDialog

from jive import helper
from jive import showFolding


class UrlFolding(QDialog, showFolding.Ui_Dialog):
    urlList = Signal(list)

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.add_shortcuts()

        self.unpackButton.clicked.connect(self.unpack)
        self.packButton.clicked.connect(self.pack)

        self.sequenceUrlClipboard.clicked.connect(self.copy_sequence_url_to_clipboard)
        self.urlListClipboard.clicked.connect(self.copy_url_list_to_clipboard)

        self.sequenceUrlClear.clicked.connect(self.clear_sequence_url)
        self.urlListClear.clicked.connect(self.clear_url_list)

        self.urlListOpen.clicked.connect(self.open_urls)
        self.sequenceUrlOpen.clicked.connect(self.unfold_and_open_urls)

        self.sequenceUrlPasteClipboard.clicked.connect(self.paste_sequence_url_from_clipboard)
        self.urlListPasteClipboard.clicked.connect(self.paste_url_list_from_clipboard)

    def unfold_and_open_urls(self) -> None:
        self.unpackButton.click()
        self.open_urls()

    def open_urls(self) -> None:
        lines = self.urlListEdit.toPlainText().splitlines()
        image_urls = helper.get_image_urls_only(lines)
        self.urlList.emit(image_urls)
        self.close()

    def clear_sequence_url(self) -> None:
        self.sequenceUrlEdit.clear()
        self.sequenceUrlEdit.setFocus()

    def clear_url_list(self) -> None:
        self.urlListEdit.clear()
        self.urlListEdit.setFocus()

    def unpack(self) -> None:
        text = self.sequenceUrlEdit.text()
        urls = helper.unfold_sequence_url(text)
        self.urlListEdit.clear()
        for line in urls:
            self.urlListEdit.appendPlainText(line)

    def pack(self) -> None:
        lines = self.urlListEdit.toPlainText().splitlines()
        lines = helper.clean(lines)

        result = helper.fold_urls(lines)
        self.sequenceUrlEdit.setText(result)

    def copy_sequence_url_to_clipboard(self) -> None:
        text = self.sequenceUrlEdit.text().strip()
        helper.copy_text_to_clipboard(text)

    def paste_sequence_url_from_clipboard(self) -> None:
        text = helper.get_text_from_clipboard()
        self.sequenceUrlEdit.setText(text)

    def copy_url_list_to_clipboard(self) -> None:
        content = self.urlListEdit.toPlainText().strip() + "\n"
        helper.copy_text_to_clipboard(content)

    def paste_url_list_from_clipboard(self) -> None:
        text = helper.get_text_from_clipboard()
        self.urlListEdit.clear()
        self.urlListEdit.appendPlainText(text)

    # def mini_log(self, text):
    #     self.miniLog.appendPlainText(text)

    def add_shortcuts(self) -> None:
        pass
