from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QShortcut

from jive import showTabs
from jive.webpage import webpage


class SimpleScrape(QDialog, showTabs.Ui_Dialog):
    urlList = Signal(list)

    def __init__(self, log):
        super().__init__()
        self.log = log
        self.setupUi(self)
        self.tabs.setCurrentIndex(0)
        self.urlLineEdit.setFocus()

        self.clearButton.clicked.connect(self.clear_url)
        self.extractButton.clicked.connect(self.extract_images)
        self.accepted.connect(self.ok_was_clicked)
        self.urlLineEdit.returnPressed.connect(self.extract_images)

        self.add_shortcuts()

    def keyPressEvent(self, evt):
        if evt.key() == Qt.Key_Return:
            return
        super().keyPressEvent(evt)

    def clear_url(self):
        self.urlLineEdit.setText("")
        self.urlLineEdit.setFocus()

    def ok_was_clicked(self):
        idx = self.tabs.currentIndex()
        if idx == 0:
            idx = 1
            self.log.info("no tab was selected, thus using Tab 1 as default")
        # print(f"current tab's index: {idx}")
        attrname = f"tab{idx}TextEdit"
        try:
            text_edit = getattr(self, attrname)    # text edit object of the current tab
            lst = text_edit.toPlainText().splitlines()
            # print(lst)
            self.urlList.emit(lst)
        except AttributeError as e:
            self.log.warning(e)

    def fill_tab(self, lst, text_edit, count_label):
        template = "Count: {0}"
        text_edit.clear()
        text_edit.setPlaceholderText("empty")
        count_label.setText(template.format(0))

        for line in lst:
            text_edit.appendPlainText(line)
        count_label.setText(template.format(len(lst)))

        for i in range(len(lst)):
            text_edit.moveCursor(QtGui.QTextCursor.Up, QtGui.QTextCursor.MoveAnchor)    # go back to top

    def extract_images(self):
        url = self.urlLineEdit.text().strip()
        distance = self.distanceSpinBox.value()
        get_links = self.getLinksCheckBox.isChecked()
        get_images = self.getImagesCheckBox.isChecked()
        #
        try:
            res = webpage.get_four_variations(url, get_links, get_images, distance)
            self.fill_tab(res[1], self.tab1TextEdit, self.tab1CountLabel)
            self.fill_tab(res[2], self.tab2TextEdit, self.tab2CountLabel)
            self.fill_tab(res[3], self.tab3TextEdit, self.tab3CountLabel)
            self.fill_tab(res[4], self.tab4TextEdit, self.tab4CountLabel)
            msg = "Done. Check the result in the other tabs!"
            self.mini_log(msg)
        except:
            msg = "couldn't extract images from the given webpage"
            self.log.warning(msg)
            self.mini_log(msg)

    def mini_log(self, text):
        self.miniLogTextEdit.appendPlainText(text)

    def add_shortcuts(self):
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

    def next_tab(self):
        number_of_tabs = self.tabs.count()
        curr = self.tabs.currentIndex()
        curr += 1
        if curr >= number_of_tabs:
            curr = number_of_tabs - 1
        self.tabs.setCurrentIndex(curr)

    def prev_tab(self):
        curr = self.tabs.currentIndex()
        curr -= 1
        if curr < 0:
            curr = 0
        self.tabs.setCurrentIndex(curr)
