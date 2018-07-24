from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QApplication, QShortcut)
from PyQt5.QtWidgets import QDialog
from functools import partial

from jive import helper
from jive import showTabs
from jive.webpage import webpage


class SimpleScrape(QDialog, showTabs.Ui_Dialog):
    urlList = Signal(list)

    def __init__(self, log) -> None:
        super().__init__()
        self.log = log
        self.setupUi(self)
        self.tabs.setCurrentIndex(0)
        self.urlLineEdit.setFocus()

        self.clearButton.clicked.connect(self.clear_url)
        self.extractButton.clicked.connect(self.extract_images)
        self.accepted.connect(self.ok_was_clicked)
        self.urlLineEdit.returnPressed.connect(self.extract_images)

        self.tabs.currentChanged.connect(self.onChange)  # changed!

        self.tab1CopyButton.clicked.connect(partial(self.copy_content_to_clipboard, 1))
        self.tab2CopyButton.clicked.connect(partial(self.copy_content_to_clipboard, 2))
        self.tab3CopyButton.clicked.connect(partial(self.copy_content_to_clipboard, 3))
        self.tab4CopyButton.clicked.connect(partial(self.copy_content_to_clipboard, 4))

        self.add_shortcuts()

    def onChange(self) -> None:
        self.update_counters()

    def copy_content_to_clipboard(self, idx: int) -> None:
        text_edit = getattr(self, f"tab{idx}TextEdit")
        text = text_edit.toPlainText().strip() + "\n"
        cb = QApplication.clipboard()
        cb.setText(text)
        msg = f"the content of Tab {idx} was copied to the clipboard"
        self.mini_log(msg)
        self.log.info(msg)

    def keyPressEvent(self, evt) -> None:
        """
        If you are on Tab 0, pressing Enter won't be equivalent
        to pressing the OK button.
        """
        if self.tabs.currentIndex() == 0:
            if evt.key() == Qt.Key_Return:
                return
        # else
        super().keyPressEvent(evt)

    def clear_url(self) -> None:
        self.urlLineEdit.setText("")
        self.urlLineEdit.setFocus()

    def ok_was_clicked(self) -> None:
        idx = self.tabs.currentIndex()
        if idx == 0:
            idx = 1
            self.log.info("no tab was selected, thus using Tab 1 as default")
        # print(f"current tab's index: {idx}")
        attrname = f"tab{idx}TextEdit"
        try:
            text_edit = getattr(self, attrname)    # text edit object of the current tab
            lines = text_edit.toPlainText().splitlines()
            image_urls = helper.get_image_urls_only(lines)
            # print(image_urls)
            self.urlList.emit(image_urls)
        except AttributeError as e:
            self.log.warning(e)

    def clear_tab(self, idx) -> None:
        text_edit = getattr(self, f"tab{idx}TextEdit")  # text edit object of the current tab
        text_edit.clear()
        self.update_counter(idx)

    def clear_tabs(self) -> None:
        for idx in range(1, 4+1):
            self.clear_tab(idx)

    def update_counter(self, idx) -> None:
        template = "Count: {0}"
        label = getattr(self, f"tab{idx}CountLabel")  # count label object of the current tab
        text_edit = getattr(self, f"tab{idx}TextEdit")  # text edit object of the current tab
        lines = text_edit.toPlainText().splitlines()
        number_of_images = len(helper.get_image_urls_only(lines))
        label.setText(template.format(number_of_images))
        tab = getattr(self, f"tab_{idx}")
        if number_of_images > 0:
            self.tabs.setTabText(self.tabs.indexOf(tab), f"Tab {idx} ({number_of_images})")
        else:
            self.tabs.setTabText(self.tabs.indexOf(tab), f"Tab {idx}")

    def update_counters(self) -> None:
        for idx in range(1, 4+1):
            self.update_counter(idx)

    def fill_tab(self, idx, lst) -> None:
        text_edit = getattr(self, f"tab{idx}TextEdit")
        self.clear_tab(idx)

        for line in lst:
            text_edit.appendPlainText(line)

        for i in range(len(lst)):
            text_edit.moveCursor(QtGui.QTextCursor.Up, QtGui.QTextCursor.MoveAnchor)    # go back to top

        self.update_counter(idx)

    def extract_images(self) -> None:
        url = self.urlLineEdit.text().strip()
        distance = self.distanceSpinBox.value()
        get_links = self.getLinksCheckBox.isChecked()
        get_images = self.getImagesCheckBox.isChecked()
        #
        try:
            res = webpage.get_four_variations(url, get_links, get_images, distance)
            self.fill_tab(1, res[1])
            self.fill_tab(2, res[2])
            self.fill_tab(3, res[3])
            self.fill_tab(4, res[4])
            self.mini_log("Done. Check the result in the other tabs!")
        except:
            msg = "couldn't extract images from the given webpage"
            self.log.warning(msg)
            self.mini_log(msg)
            self.clear_tabs()

    def mini_log(self, text) -> None:
        self.miniLogTextEdit.appendPlainText(text)

    def add_shortcuts(self) -> None:
        key = "Alt+Right"
        self.nextTabShortcut = QShortcut(QKeySequence(key), self)
        self.nextTabShortcut.activated.connect(self.next_tab)
        key = "Ctrl+PgDown"
        self.nextTabShortcut2 = QShortcut(QKeySequence(key), self)
        self.nextTabShortcut2.activated.connect(self.next_tab)

        key = "Alt+Left"
        self.prevTabShortcut = QShortcut(QKeySequence(key), self)
        self.prevTabShortcut.activated.connect(self.prev_tab)
        key = "Ctrl+PgUp"
        self.prevTabShortcut2 = QShortcut(QKeySequence(key), self)
        self.prevTabShortcut2.activated.connect(self.prev_tab)

    def next_tab(self) -> None:
        number_of_tabs = self.tabs.count()
        curr = self.tabs.currentIndex()
        curr += 1
        if curr >= number_of_tabs:
            curr = number_of_tabs - 1
        self.tabs.setCurrentIndex(curr)

    def prev_tab(self) -> None:
        curr = self.tabs.currentIndex()
        curr -= 1
        if curr < 0:
            curr = 0
        self.tabs.setCurrentIndex(curr)
