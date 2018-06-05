#!/usr/bin/env python3

# check compatibility
try:
    eval('f"{1+1}"')
except SyntaxError:
    raise ImportError("The application requires Python 3.6+")

import os
import random
import sys
from exceptions import ImageError
from functools import partial
from pathlib import Path

import requests
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QKeySequence, QPixmap, QContextMenuEvent, QMouseEvent, QCursor
from PyQt5.QtWidgets import (QAction, QApplication, QDesktopWidget,
                             QFileDialog, QFrame, QInputDialog, QLabel,
                             QLineEdit, QMainWindow, QMenu, QMessageBox,
                             QScrollArea, QShortcut, QVBoxLayout)

import categories
import config as cfg
import helper
import mylogging as log
import settings
import shortcuts as scuts
import statusbar as sbar
from extractors import imgur, subreddit, tumblr
from helper import bold, gray, green, red
from imageview import ImageView

OFF = False
ON = True

# TEST_IMG = "pinup.jpg"
# TEST_IMG = "girl.jpg"
# TEST_IMG = "burned_man.jpg"

# TEST_DIR = "/trash/images"
# TEST_DIR = "samples/"
# TEST_DIR = "/trash/image_viewer"

# TEST_SUBREDDIT = "EarthPorn"
# TEST_SUBREDDIT = "hardbodies"

# TEST_IMGUR_ALBUM = "https://imgur.com/gallery/9p0gCyv"    # pirates
# TEST_REMOTE_URL_FILE = "https://i.imgur.com/k489QN8.jpg"    # femme pirate
# TEST_TUMBLR_POST = "https://different-landscapes.tumblr.com/post/174158537319"    # tree

class ImageProperty:
    """
    Properties of the current (previous / next) image(s).
    """
    IMAGE_STATE_OK = 1
    IMAGE_STATE_PROBLEM = 2

    def __init__(self, name, parent):
        self.name = name
        self.local_file = self._is_local_file(name)
        self.parent = parent
        self.zoom_ratio = 1.0
        self.original_img = None    # will be set in read()
        self.image_state = None     # will be set in read()
        self.zoomed_img = None      # will be set in read()
        self.file_size = -1         # will be set in read()

    @classmethod
    def to_pixmap(cls, name):
        try:
            pm = None
            file_size = -1
            if os.path.isfile(name):
                pm = QPixmap(name)
                file_size = os.path.getsize(name)
            else:
                if name.startswith(("http://", "https://")):
                    url = name
                    r = requests.get(url, headers=cfg.headers)
                    data = r.content
                    pm = QPixmap()
                    pm.loadFromData(data)
                    file_size = int(r.headers['Content-Length'])
            #
            if pm is None or pm.width() == 0:
                raise ImageError
            # else
            return (pm, cls.IMAGE_STATE_OK, file_size)
        except:
            log.warning(f"cannot read the image {name}")
            return (QPixmap(str(Path(cfg.ASSETS_DIR, "not_found.png"))), cls.IMAGE_STATE_PROBLEM, -1)

    def read(self):
        """
        Construct the pixmap for the current image.
        """
        self.original_img, self.image_state, self.file_size = self.to_pixmap(self.name)
        self.calculate_zoomed_image()
        return self

    def free(self):
        """
        Call it when you switch to another image, thus you can free the memory
        occupied by the pixmaps (original and zoomed ones).
        """
        self.original_img = None
        self.zoomed_img = None

    def _is_local_file(self, name):
        return os.path.isfile(name)

    def zoom_in(self):
        self.zoom_ratio *= 1.1
        self.calculate_zoomed_image()

    def zoom_out(self):
        self.zoom_ratio *= 0.9
        self.calculate_zoomed_image()

    def calculate_zoomed_image(self):
        self.zoomed_img = self.original_img.scaled(self.zoom_ratio * self.original_img.width(),
                                                   self.zoom_ratio * self.original_img.height(),
                                                   Qt.KeepAspectRatio,
                                                   Qt.SmoothTransformation)

    def set_zoomed_img(self, pm):
        self.zoomed_img = pm
        # If there's a problem with an image, we return not_found.png,
        # thus division by 0 cannot happen here.
        self.zoom_ratio = pm.width() / self.original_img.width()

    def zoom_reset(self):
        self.zoom_ratio = 1.0
        self.zoomed_img = self.original_img

    def fit_img_to_window(self):
        width, height = self.parent.available_width_and_height()
        pm = self.original_img.scaled(width,
                                      height,
                                      Qt.KeepAspectRatio,
                                      Qt.SmoothTransformation)
        self.set_zoomed_img(pm)

    def fit_img_to_window_width(self):
        window_width = self.parent.geometry().width()
        new_width = window_width * (cfg.IMG_WIDTH_TO_WINDOW_WIDTH_IN_PERCENT / 100)
        new_height = new_width / self.get_aspect_ratio()
        pm = self.original_img.scaled(new_width,
                                      new_height,
                                      Qt.KeepAspectRatio,
                                      Qt.SmoothTransformation)
        self.set_zoomed_img(pm)

    def get_file_name_only(self):
        return str(Path(self.name).name)

    def get_file_name_or_url(self):
        if self.local_file:
            return str(Path(self.name).name)
        else:
            return self.name

    def get_absolute_path_or_url(self):
        if self.local_file:
            return str(Path(self.name).absolute())
        else:
            return self.name

    def get_aspect_ratio(self):
        return self.original_img.width() / self.original_img.height()

# end class ImageProperty


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.title = "JiVE"
        self.top = 50
        self.left = 50
        self.width = 900
        self.height = 600

        self.prev_random_img_idx = -1

        self.auto_fit = False
        self.auto_width = False
        self.mouse_pointer = ON
        self.show_image_path = True

        self.settings = settings.Settings()

        self.setMouseTracking(True)

        self.setAcceptDrops(True)    # enable drag & drop

        self._fit_window_to_image_status = OFF
        self._fit_window_to_image_width = None     # will be set later
        self._fit_window_to_image_height = None    # will be set later

        self.list_of_images = []
        self.curr_img_idx = -1
        self.curr_img = None

        self.shortcuts = scuts.Shortcuts()
        self.add_shortcuts()

        self.init_ui()

        self.toggle_auto_fit()           # set it ON and show the flash message
        self.toggle_show_image_path()    # make it False and hide it

        self.reset()    # it must be last thing here

        # These are here after reset() just for testing.
        # TO BE REMOVED in the release version.
        # self.open_local_dir(TEST_DIR)
        # self.open_subreddit(TEST_SUBREDDIT)
        # self.open_imgur_album(TEST_IMGUR_ALBUM)
        # self.open_remote_url_file(TEST_REMOTE_URL_FILE)
        # self.open_tumblr_post(TEST_TUMBLR_POST)

    def reset(self, msg=None):
        self.list_of_images = []
        self.curr_img_idx = -1
        self.curr_img = None

        if self.curr_img is None:
            self.show_logo()

        self.info_line.setText("")
        self.statusbar.reset()
        if msg:
            self.statusbar.flash_message(msg)
        #
        # if the categories.yaml was changed
        self.create_contextmenu()

    # def mousePressEvent(self, QMouseEvent):
    #     print(QMouseEvent.pos())

    def mouseReleaseEvent(self, QMouseEvent):
        p = QMouseEvent.pos()
        x, y = p.x(), p.y()
        # print(x, y)
        width = self.img_view.width()
        if x < width * (1 / 3):
            self.jump_to_prev_image()
            # print("prev")
        if x > width * (2 / 3):
            self.jump_to_next_image()
            # print("next")

    def set_title(self, prefix=""):
        if prefix:
            self.setWindowTitle(f"{prefix} - {self.title}")

    def open_local_dir(self, local_folder, redraw=False):
        self.list_of_images = self.read_local_dir(local_folder)
        if len(self.list_of_images) == 0:
            log.warning("no images were found")
            return
        # else
        self.curr_img_idx = 0
        self.curr_img = self.list_of_images[0].read()
        #
        if redraw:
            self.redraw()

    def open_local_file(self, local_file, redraw=False):
        self.list_of_images = self.read_local_dir(str(Path(local_file).parent))
        if len(self.list_of_images) == 0:
            log.warning("no images were found")
            return
        # else
        for i in range(len(self.list_of_images)):
            if self.list_of_images[i].name == local_file:
                self.curr_img_idx = i
                break
        self.curr_img = self.list_of_images[self.curr_img_idx].read()
        #
        if redraw:
            self.redraw()

    def open_local_file_or_dir(self, name):
        p = Path(name)
        if p.is_file():
            self.open_local_file(str(p), redraw=True)
        if p.is_dir():
            self.open_local_dir(str(p), redraw=True)

    def open_remote_url_file(self, url):
        if Path(url).suffix.lower() not in cfg.SUPPORTED_FORMATS:
            log.warning("unsupported file format")
            return
        # else
        self.list_of_images = [ImageProperty(url, self)]
        self.curr_img_idx = 0
        self.curr_img = self.list_of_images[0].read()

    def open_subreddit(self, text, redraw=False):
        subreddit_name = subreddit.get_subreddit_name(text)
        if not subreddit_name:
            log.warning("that's not a subreddit")
            return
        # else
        urls = subreddit.read_subreddit(subreddit_name, self.statusbar)
        if len(urls) == 0:
            log.warning("no images could be extracted")
            self.statusbar.flash_message(red("no images found"))
            return
        # else
        self.list_of_images = [ImageProperty(url, self) for url in urls]
        self.curr_img_idx = 0
        self.curr_img = self.list_of_images[0].read()
        #
        if redraw:
            self.redraw()

    def open_imgur_album(self, text):
        urls = []
        if imgur.is_album(text):
            images = imgur.extract_images_from_an_album(text)
            for img_url in images:
                if Path(img_url).suffix.lower() in cfg.SUPPORTED_FORMATS:
                    urls.append(img_url)
                #
            #
        else:
            log.warning("that's not an Imgur album")
        self.list_of_images = [ImageProperty(url, self) for url in urls]
        if len(self.list_of_images) > 0:
            self.curr_img_idx = 0
            self.curr_img = self.list_of_images[0].read()

    def open_tumblr_post(self, text):
        urls = []
        if tumblr.is_post(text):
            url = text
            images = tumblr.extract_images_from_a_specific_post(url)
            for img_url in images:
                if Path(img_url).suffix.lower() in cfg.SUPPORTED_FORMATS:
                    urls.append(img_url)
                #
            #
        else:
            log.warning("that's not a tumblr post")
        self.list_of_images = [ImageProperty(url, self) for url in urls]
        if len(self.list_of_images) > 0:
            self.curr_img_idx = 0
            self.curr_img = self.list_of_images[0].read()

    def jump_to_next_image(self):
        if self.curr_img_idx == len(self.list_of_images) - 1:
            self.statusbar.flash_message(red("no more"), wait=cfg.MESSAGE_FLASH_TIME_1)
            return
        # else
        new_idx = self.curr_img_idx + 1
        if new_idx >= len(self.list_of_images):
            new_idx = 0
        #
        self.jump_to_image(new_idx)

    def jump_to_first_image(self):
        self.jump_to_image(0)

    def jump_to_last_image(self):
        new_idx = len(self.list_of_images) - 1
        self.jump_to_image(new_idx)

    def jump_to_prev_image(self):
        if self.curr_img_idx == 0:
            self.statusbar.flash_message(red("no less"), wait=cfg.MESSAGE_FLASH_TIME_1)
            return
        # else
        new_idx = self.curr_img_idx - 1
        if new_idx < 0:
            new_idx = len(self.list_of_images) - 1
        #
        self.jump_to_image(new_idx)

    def jump_five_percent_forward(self):
        offset = round(5 * len(self.list_of_images) / 100)
        self.jump_to_image(self.curr_img_idx + offset)

    def jump_five_percent_backward(self):
        offset = round(5 * len(self.list_of_images) / 100)
        self.jump_to_image(self.curr_img_idx - offset)

    def jump_to_image(self, new_idx):
        old_idx = self.curr_img_idx
        if old_idx == new_idx:
            return
        self.curr_img_idx = new_idx
        #
        if self.curr_img_idx >= len(self.list_of_images):
            self.curr_img_idx = len(self.list_of_images) - 1
        if self.curr_img_idx < 0:
            self.curr_img_idx = 0
        #
        self.curr_img = self.list_of_images[self.curr_img_idx].read()
        if old_idx != self.curr_img_idx:
            self.list_of_images[old_idx].free()  # don't forget to free it!
        self.scroll_to_top()
        self.redraw()

    def jump_to_random_image(self):
        if len(self.list_of_images) > 1:
            # always choose a different image:
            while True:
                idx = random.randrange(len(self.list_of_images))
                if idx != self.curr_img_idx:
                    break
                #
            #
            self.prev_random_img_idx = self.curr_img_idx    # save where we were
            self.jump_to_image(idx)

    def jump_to_prev_random_image(self):
        if self.prev_random_img_idx == -1:
            return
        # else
        jump_to = self.prev_random_img_idx
        self.prev_random_img_idx = self.curr_img_idx  # save where we were
        self.jump_to_image(jump_to)

    def read_local_dir(self, dir_path):
        lst = helper.read_image_files(dir_path)
        return [ImageProperty(img, self) for img in lst]    # without .read()

    def init_ui(self):
        # Option 1:
        self.setGeometry(self.top, self.left, self.width, self.height)
        # Option 2:
        # self.center()
        # self.resize(self.width, self.height)

        self.setWindowTitle(self.title)
        self.setWindowIcon(QtGui.QIcon(cfg.ICON))

        self.img_view = ImageView(self)
        # self.central_widget.setStyleSheet("background-color: black")
        # black background

        # self.central_widget.setBackgroundBrush(Qt.black)
        # self.central_widget.setStyleSheet("background-color: black")
        self.setCentralWidget(self.img_view)

        self.scroll = QScrollArea()
        self.scroll.setFrameShape(QFrame.NoFrame)    # no border in fullscreen mode
        self.image_label = QLabel()
        self.scroll.setAlignment(Qt.AlignCenter)
        self.scroll.setWidget(self.image_label)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll)

        self.img_view.setLayout(layout)

        self.info_line = QLabel(self.img_view)
        self.info_line.setMinimumWidth(cfg.LONG)
        self.info_line.move(20, 10)
        self.info_line.show()

        self.path_line = QLabel(self.img_view)
        self.path_line.setMinimumWidth(cfg.LONG)
        self.path_line.move(20, 30)
        self.path_line.show()

        self.statusbar = sbar.StatusBar(self)
        self.statusBar().setStyleSheet(cfg.TOP_AND_BOTTOM_BAR_STYLESHEET)
        self.statusBar().addWidget(self.statusbar, 1)

        # self.set_current_image(TEST_IMG)

        self.show_image()
        self.make_scrollbars_disappear()
        # self.fit_window_to_image()

        self.create_menu_actions()
        self.create_contextmenu()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_contextmenu)

        self.create_menubar()

    def show_scrollbars(self):
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def hide_scrollbars(self):
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def make_scrollbars_disappear(self):
        self.resize(self.geometry().width(),
                    self.geometry().height())

    def center(self):
        # geometry of the main window
        qr = self.frameGeometry()

        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()

        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)

        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())

    def menu_open_subreddit(self):
        text, okPressed = QInputDialog.getText(self, "Open subreddit", "Subreddit's name or its URL:", QLineEdit.Normal, "")
        text = text.strip()
        if okPressed and text:
            self.open_subreddit(text, redraw=True)
            # self.redraw()

    def menu_open_imgur_album(self):
        text, okPressed = QInputDialog.getText(self,
                                               "Open Imgur album",
                                               "Complete URL:",
                                               QLineEdit.Normal,
                                               "")
        text = text.strip()
        if okPressed and text:
            self.open_imgur_album(text)
            self.redraw()

    def menu_open_tumblr_post(self):
        text, okPressed = QInputDialog.getText(self,
                                               "Open Tumblr post",
                                               "Complete URL:" + " " * 100,
                                               QLineEdit.Normal,
                                               "")
        text = text.strip()
        if okPressed and text:
            self.open_tumblr_post(text)
            self.redraw()

    def menu_open_url_auto_detect(self):
        text, okPressed = QInputDialog.getText(self,
                                               "Auto detect URL",
                                               "URL / subreddit / etc.:" + " " * 80,
                                               QLineEdit.Normal,
                                               self.settings.get_last_open_url_auto_detect())
        text = text.strip()
        if okPressed and text:
            self.auto_detect_and_open(text)

    def auto_detect_and_open(self, text):
        self.settings.set_last_open_url_auto_detect(text)
        # Is it a remote image's URL?
        if Path(text).suffix.lower() in cfg.SUPPORTED_FORMATS:
            log.info("it seems to be a remote image")
            self.open_remote_url_file(text)
            self.redraw()
            return
        # Is it a subreddit?
        res = subreddit.get_subreddit_name(text)
        if res:
            log.info("it seems to be a subreddit")
            self.open_subreddit(text, redraw=True)
            # self.redraw()
            return
        # else, is it an imgur album?
        if imgur.is_album(text):
            log.info("it seems to be an Imgur album")
            self.open_imgur_album(text)
            self.redraw()
            return
        # else, is it a tumblr post?
        if tumblr.is_post(text):
            log.info("it seems to be a Tumblr post")
            self.open_tumblr_post(text)
            self.redraw()
            return
        else:
            log.warning("hmm, it seems to be something new...")

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        text = event.mimeData().text().strip()
        if text.startswith("file://"):
            text = text[len("file://"):]
        self.open_local_file_or_dir(text)
        log.debug("dropEvent: {}".format(event.mimeData().text()))

    #########################
    ## BEGIN: top menu bar ##
    #########################
    def create_menu_actions(self):
        key = "Ctrl+O"
        self.open_file_act = QAction("Open &file", self)
        self.shortcuts.register_menubar_action(key, self.open_file_act, self.open_file)
        #
        key = "Ctrl+D"
        self.open_dir_act = QAction("Open &directory", self)
        self.shortcuts.register_menubar_action(key, self.open_dir_act, self.open_dir)
        #
        key = "Ctrl+U"
        self.open_url_auto_detect_act = QAction("Auto detect &URL", self)
        self.shortcuts.register_menubar_action(key, self.open_url_auto_detect_act, self.menu_open_url_auto_detect)
        #
        self.open_url_open_subreddit_act = QAction("Open sub&reddit", self)
        self.open_url_open_subreddit_act.triggered.connect(self.menu_open_subreddit)
        self.open_url_open_imgur_album_act = QAction("Open &Imgur album", self)
        self.open_url_open_imgur_album_act.triggered.connect(self.menu_open_imgur_album)
        self.open_url_open_tumblr_post_act = QAction("Open &Tumblr post", self)
        self.open_url_open_tumblr_post_act.triggered.connect(self.menu_open_tumblr_post)
        #
        self.save_image_act = QAction("Save image", self)
        # self.save_image_act.triggered.connect(self.save_image)
        #
        self.image_info_act = QAction("View image info", self)
        # self.image_info_act.triggered.connect(self.image_info)
        #
        self.slideshow_act = QAction("Slideshow", self)
        # self.slideshow_act.triggered.connect(self.slideshow)
        #
        self.help_act = QAction("&Help", self)
        # self.help_act.triggered.connect(self.help)
        #
        self.about_act = QAction("&About", self)
        self.about_act.triggered.connect(self.open_about)
        #
        key = "Ctrl+Alt+R"
        self.reset_act = QAction("&Reset", self)
        self.shortcuts.register_menubar_action(key, self.reset_act, partial(self.reset, "reset"))
        #
        key = "Q"
        self.quit_act = QAction("&Quit", self)
        self.shortcuts.register_menubar_action(key, self.quit_act, self.close)
        #
        key = "Alt+M"
        self.hide_menubar_act = QAction("Hide menu bar", self)
        self.shortcuts.register_menubar_action(key, self.hide_menubar_act, self.toggle_menubar)
        #
        key = "Ctrl+M"
        self.show_mouse_pointer_act = QAction("Show mouse pointer", self, checkable=True, checked=True)
        self.shortcuts.register_menubar_action(key, self.show_mouse_pointer_act, self.toggle_mouse_pointer)

    def create_menubar(self):
        self.menubar = self.menuBar()
        self.shortcuts.disable_conflicting_window_shortcuts()
        # self.menubar.setStyleSheet(cfg.TOP_AND_BOTTOM_BAR_STYLESHEET)

        open_url_acts = [self.open_url_auto_detect_act,
                         cfg.SEPARATOR,
                         self.open_url_open_subreddit_act,
                         self.open_url_open_imgur_album_act,
                         self.open_url_open_tumblr_post_act]

        fileMenu = self.menubar.addMenu("&File")
        viewMenu = self.menubar.addMenu("&View")

        # fileMenu
        fileMenu.addAction(self.open_file_act)
        fileMenu.addAction(self.open_dir_act)
        open_url_menu = QMenu(self.menubar)
        open_url_menu.setTitle("Open &URL")
        fileMenu.addMenu(open_url_menu)
        for entry in open_url_acts:
            if isinstance(entry, str):
                open_url_menu.addSeparator()
            else:
                open_url_menu.addAction(entry)
        #
        fileMenu.addSeparator()
        fileMenu.addAction(self.reset_act)
        fileMenu.addAction(self.quit_act)

        # viewMenu
        viewMenu.addAction(self.hide_menubar_act)
        viewMenu.addAction(self.show_mouse_pointer_act)
    #
    #######################
    ## END: top menu bar ##
    #######################

    #################################
    ## BEGIN: popup (context) menu ##
    #################################
    def create_contextmenu(self):
        self.menu = QMenu(self)

        open_url_acts = [self.open_url_auto_detect_act,
                         cfg.SEPARATOR,
                         self.open_url_open_subreddit_act,
                         self.open_url_open_imgur_album_act,
                         self.open_url_open_tumblr_post_act]

        # When I right-click, very often the first menu gets selected.
        # "Nothing" is added to avoid that problem.
        self.menu.addAction(QAction("Nothing", self))
        self.menu.addSeparator()
        self.menu.addAction(self.open_file_act)
        self.menu.addAction(self.open_dir_act)
        open_url_menu = QMenu(self.menu)
        open_url_menu.setTitle("Open &URL")
        self.menu.addMenu(open_url_menu)
        for entry in open_url_acts:
            if isinstance(entry, str):
                open_url_menu.addSeparator()
            else:
                open_url_menu.addAction(entry)
        # self.menu.addAction(self.open_url_act)
        open_subreddit_categories = QMenu(self.menu)
        open_subreddit_categories.setTitle("Select subreddit...")
        self.menu.addMenu(open_subreddit_categories)
        categories.Categories(self, open_subreddit_categories, self.open_subreddit).populate()
        self.menu.addAction(self.save_image_act)
        self.menu.addSeparator()
        self.menu.addAction(self.image_info_act)
        self.menu.addAction(self.slideshow_act)
        self.menu.addSeparator()
        self.menu.addAction(self.help_act)
        self.menu.addAction(self.about_act)
        self.menu.addAction(self.quit_act)

    def show_contextmenu(self, pos):
        self.menu.popup(self.mapToGlobal(pos))
    #
    ###############################
    ## END: popup (context) menu ##
    ###############################

    def open_dir(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folder = QFileDialog.getExistingDirectory(self,
                                                  caption="Open Image Directory",
                                                  directory=self.settings.get_last_dir_opened(),
                                                  options=options)
        if os.path.isdir(folder):
            self.open_local_dir(folder)
            self.settings.set_last_dir_opened(folder)
            self.redraw()

    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filter = "Images (*.bmp *.jpg *.jpe *.jpeg *.png *.pbm *.pgm *.ppm *.xbm *.xpm)"
        file_obj = QFileDialog.getOpenFileName(self,
                                               caption="Open Image File",
                                               directory=str(Path(self.settings.get_last_file_opened()).parent),
                                               filter=filter,
                                               initialFilter=filter,
                                               options=options)
        fname = file_obj[0]
        if os.path.isfile(fname):
            self.open_local_file(fname)
            self.settings.set_last_file_opened(fname)
            self.redraw()

    def add_shortcuts(self):
        key = "Ctrl+O"
        self.shortcutOpenFile = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutOpenFile, self.open_file)

        key = "Ctrl+D"
        self.shortcutOpenDir = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutOpenDir, self.open_dir)

        key = "Q"
        self.shortcutQuit = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutQuit, self.close)

        key = "Ctrl+U"
        self.shortcutAutoDetect = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutAutoDetect, self.menu_open_url_auto_detect)

        key = "Z"
        self.shortcutFitWindowToImage = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutFitWindowToImage, self.toggle_fit_window_to_image)

        key = "F11"
        self.shortcutFullscreen = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutFullscreen, self.toggle_fullscreen)

        key = "+"
        self.shortcutZoomIn = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutZoomIn, self.zoom_in)

        key = "-"
        self.shortcutZoomOut = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutZoomOut, self.zoom_out)

        key = "="
        self.shortcutZoomReset = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutZoomReset, self.zoom_reset)

        key = "M"
        self.shortcutMaximized = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutMaximized, self.toggle_maximized)

        key = "F"
        self.shortcutFitImageToWindow = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutFitImageToWindow, self.fit_image_to_window)
        #
        key = "W"
        self.shortcutFitImageToWindowWidth = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutFitImageToWindowWidth, self.fit_image_to_window_width)

        key = "Left"
        self.shortcutPrevImage = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutPrevImage, self.jump_to_prev_image)
        #
        key ="PgUp"
        self.shortcutNextImagePgUp = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutNextImagePgUp, self.jump_five_percent_backward)

        #####################
        ## BEGIN scrolling ##
        #####################
        key = "Shift+Down"
        self.shortcutScrollDown = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutScrollDown, self.scroll_down)
        key = "2"
        self.shortcutScrollDownNum = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutScrollDownNum, self.scroll_down)
        key = "Down"
        self.shortcutScrollDownArrow = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutScrollDownArrow, self.scroll_down)
        #
        key ="Shift+Up"
        self.shortcutScrollUp = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutScrollUp, self.scroll_up)
        key = "8"
        self.shortcutScrollUpNum = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutScrollUpNum, self.scroll_up)
        key = "Up"
        self.shortcutScrollUpArrow = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutScrollUpArrow, self.scroll_up)
        #
        key = "Shift+Right"
        self.shortcutScrollRight = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutScrollRight, self.scroll_right)
        key = "6"
        self.shortcutScrollRightNum = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutScrollRightNum, self.scroll_right)
        #
        key = "Shift+Left"
        self.shortcutScrollLeft = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutScrollLeft, self.scroll_left)
        key = "4"
        self.shortcutScrollLeftNum = QShortcut(QKeySequence("4"), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutScrollLeftNum, self.scroll_left)
        ###################
        ## END scrolling ##
        ###################

        key = "Right"
        self.shortcutNextImage = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutNextImage, self.jump_to_next_image)
        #
        key = "PgDown"
        self.shortcutNextImagePgDn = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutNextImagePgDn, self.jump_five_percent_forward)

        key = "Home"
        self.shortcutFirstImage = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutFirstImage, self.jump_to_first_image)

        key = "End"
        self.shortcutLastImage = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutLastImage, self.jump_to_last_image)

        key = "Ctrl+F"
        self.shortcutAutoFit = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutAutoFit, self.toggle_auto_fit)
        #
        key = "Ctrl+w"
        self.shortcutAutoWidth = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutAutoWidth, self.toggle_auto_width)

        key = "Ctrl+M"
        self.shortcutHideMouse = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutHideMouse, self.toggle_mouse_pointer)

        key = "R"
        self.shortcutJumpToRandomImg = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutJumpToRandomImg, self.jump_to_random_image)
        #
        key = "Shift+R"
        self.shortcutJumpToPrevRandomImg = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutJumpToPrevRandomImg, self.jump_to_prev_random_image)

        key = "P"
        self.shortcutToggleShowImagePath = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutToggleShowImagePath, self.toggle_show_image_path)

        key = "Shift+P"
        self.shortcutCopyPathToClipboard = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutCopyPathToClipboard, self.copy_path_to_clipboard)

        key = "G"
        self.shortcutGoToImage = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutGoToImage, self.dialog_go_to_image)

        key = "Ctrl+Alt+R"
        self.shortcutReset = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutReset, partial(self.reset, "reset"))

        key = "Alt+M"
        self.shortcutToggleMenubar = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutToggleMenubar, self.toggle_menubar)

        key = "Menu"
        self.shortcutContextMenu = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutContextMenu, self.show_popup)

    def show_popup(self):
        """
        When the "Menu" key is pressed, show the context menu right at the mouse pointer.
        """
        p = QCursor.pos()
        x, y = p.x(), p.y()
        qr = self.frameGeometry()
        top_left = qr.topLeft()
        x_offset, y_offset = top_left.x(), top_left.y()
        self.menu.popup(self.mapToGlobal(QPoint(x - x_offset, y - y_offset - self.menuBar().height())))

    def toggle_menubar(self):
        if self.menubar.isVisible():
            self.menubar.hide()
            self.statusbar.flash_message("Alt+M: show menu bar")
            self.shortcuts.enable_all_window_shortcuts()
        else:
            self.menubar.show()
            self.shortcuts.disable_conflicting_window_shortcuts()
        self.redraw()

    def dialog_go_to_image(self):
        total = len(self.list_of_images)
        if total == 0:
            self.statusbar.flash_message(red("Where to? It's empty."))
            return
        # else
        text, okPressed = QInputDialog.getText(self, "Go To Image", f"Enter a value between 1 and {total}:", QLineEdit.Normal, "")
        if okPressed and text:
            try:
                value = int(text)
                if not (1 <= value <= total):
                    raise ValueError
                # else
                idx = value - 1
                self.jump_to_image(idx)
            except ValueError:
                self.statusbar.flash_message(red("invalid value"))

    def scroll_to_top(self):
        self.scroll.verticalScrollBar().setValue(0)

    def scroll_down(self):
        val = self.scroll.verticalScrollBar().value()
        self.scroll.verticalScrollBar().setValue(val + 100)

    def scroll_right(self):
        val = self.scroll.horizontalScrollBar().value()
        self.scroll.horizontalScrollBar().setValue(val + 100)

    def scroll_up(self):
        val = self.scroll.verticalScrollBar().value()
        self.scroll.verticalScrollBar().setValue(val - 100)

    def scroll_left(self):
        val = self.scroll.horizontalScrollBar().value()
        self.scroll.horizontalScrollBar().setValue(val - 100)

    def copy_path_to_clipboard(self):
        text = self.curr_img.get_absolute_path_or_url()
        cb = QApplication.clipboard()
        cb.setText(text)
        msg = "{0} copied to clipboard".format("path" if self.curr_img.local_file else "URL")
        self.statusbar.flash_message(msg, wait=cfg.MESSAGE_FLASH_TIME_3)

    def toggle_show_image_path(self):
        if self.show_image_path:
            self.show_image_path = False
            self.path_line.hide()
        else:
            self.show_image_path = True
            self.path_line.show()

    def toggle_mouse_pointer(self):
        if self.mouse_pointer == ON:
            self.setCursor(Qt.BlankCursor)  # hide cursor
            self.mouse_pointer = OFF
            self.statusbar.flash_message("Ctrl+M: show mouse pointer")
        else:
            self.unsetCursor()
            self.mouse_pointer = ON
            # self.statusbar.flash_message("show mouse cursor")

    # auto_fit and auto_width are not compatible
    # choose only one of them
    # if one of them is enabled, the other must be disabled

    def toggle_auto_fit(self):
        self.auto_fit = not self.auto_fit
        if self.auto_fit:
            self.auto_width = False    # disable the other
            self.statusbar.mode_label.setText(bold("AUTO FIT ON"))
            self.hide_scrollbars()
        else:
            self.statusbar.mode_label.setText(gray("AUTO FIT OFF"))
            self.show_scrollbars()
        self.redraw()

    def toggle_auto_width(self):
        self.auto_width = not self.auto_width
        if self.auto_width:
            self.auto_fit = False    # disable the other
            self.statusbar.mode_label.setText(bold("AUTO WIDTH {0}%".format(cfg.IMG_WIDTH_TO_WINDOW_WIDTH_IN_PERCENT)))
        else:
            self.statusbar.mode_label.setText(gray("AUTO WIDTH OFF"))
        self.redraw()

    def zoom_in(self):
        if self.auto_fit or self.auto_width:
            self.statusbar.flash_message(red("oops, auto stuff is on"))
            return
        # else
        self.statusbar.flash_message("zoom in")
        self.curr_img.zoom_in()
        self.redraw()

    def zoom_out(self):
        if self.auto_fit or self.auto_width:
            self.statusbar.flash_message(red("oops, auto stuff is on"))
            return
        # else
        self.statusbar.flash_message("zoom out")
        self.curr_img.zoom_out()
        self.redraw()

    def zoom_reset(self):
        if self.auto_fit or self.auto_width:
            self.statusbar.flash_message(red("oops, auto stuff is on"))
            return
        # else
        self.statusbar.flash_message("reset zoom")
        self.curr_img.zoom_reset()
        self.redraw()

    def open_about(self):
        QMessageBox.about(self, "About", f"Jabba's Image Viewer {cfg.VERSION}")

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.statusBar().show()
            self.menubar.show()
        else:
            self.showFullScreen()
            self.statusBar().hide()
            self.menubar.hide()

    def toggle_fit_window_to_image(self):
        if self._fit_window_to_image_status == OFF:
            self._fit_window_to_image_width = self.geometry().width()
            self._fit_window_to_image_height = self.geometry().height()
            #
            self.resize(self.curr_img.zoomed_img.width(),
                        self.curr_img.zoomed_img.height())
            self._fit_window_to_image_status = ON
        else:
            self.resize(self._fit_window_to_image_width,
                        self._fit_window_to_image_height)
            self._fit_window_to_image_status = OFF

    def fit_image_to_window(self):
        if self.auto_width:
            self.statusbar.flash_message(red("oops, auto width is on"))
            return
        # else
        self.statusbar.flash_message("fit to window")
        self.curr_img.fit_img_to_window()
        self.redraw()

    def fit_image_to_window_width(self):
        if self.auto_fit:
            self.statusbar.flash_message(red("oops, auto fit is on"))
            return
        # else
        self.statusbar.flash_message("fit width")
        self.curr_img.fit_img_to_window_width()
        self.redraw()

    def toggle_maximized(self):
        if self.isFullScreen():
            self.toggle_fullscreen()    # back to normal
            self.toggle_maximized()     # maximize it
            return    # stop recursion, keep it maximized
        #
        if not self.isMaximized():
            self.showMaximized()
            self.statusbar.flash_message("maximized")
        else:
            self.showNormal()
            self.statusbar.flash_message("un-maximized")

    def resizeEvent(self, event):
        self.redraw()

    def show_logo(self):
        scale = 0.3
        pm = ImageProperty.to_pixmap(cfg.LOGO)[0]
        pm = pm.scaled(self.geometry().width() * scale,
                       self.geometry().height() * scale,
                       Qt.KeepAspectRatio,
                       Qt.SmoothTransformation)
        self.image_label.setPixmap(pm)
        self.image_label.resize(pm.width(), pm.height())

    def available_width_and_height(self):
        """
        Available width and height for the images.
        """
        width, height = self.img_view.width(), self.img_view.height()
        #
        if not self.menubar.isVisible():
            height += self.menubar.height()
        if not self.statusbar.isVisible():
            height += self.statusbar.height()
        #
        return width, height

    def show_image(self):
        if self.curr_img is None:
            return
        #
        pm = self.curr_img.original_img.scaled(self.curr_img.zoom_ratio * self.geometry().width(),
                                               self.curr_img.zoom_ratio * self.geometry().height(),
                                               Qt.KeepAspectRatio,
                                               Qt.SmoothTransformation)
        # avoid upscale
        if pm.width() > self.curr_img.original_img.width() or pm.height() > self.curr_img.original_img.height():
            pm = self.curr_img.original_img
        self.curr_img.set_zoomed_img(pm)
        self.redraw()

    def redraw(self):
        # log.info("redraw")
        #
        if self.curr_img is None:
            return
        #
        if self.auto_fit:
            self.curr_img.fit_img_to_window()
        if self.auto_width:
            self.curr_img.fit_img_to_window_width()
        pm = self.curr_img.zoomed_img
        self.image_label.setPixmap(pm)
        self.image_label.resize(pm.width(), pm.height())
        #
        resolution = "{w} x {h}".format(w=self.curr_img.original_img.width(), h=self.curr_img.original_img.height())
        file_size = helper.file_size_fmt(self.curr_img.file_size) if self.curr_img.file_size > -1 else ""
        zoom = int(self.curr_img.zoom_ratio * 100)
        #
        self.info_line.setText(green("{0} of {1}".format(self.curr_img_idx + 1, len(self.list_of_images))))
        #
        self.path_line.setText(green(self.curr_img.get_file_name_or_url()))
        #
        self.statusbar.curr_pos_label.setText("{0} of {1}".format(self.curr_img_idx + 1, len(self.list_of_images)))
        self.statusbar.file_name_label.setText("{0}    {1}".format(helper.shorten(self.curr_img.get_file_name_or_url()),
                                                                file_size))
        self.statusbar.resolution_label.setText(f"{resolution} @ {zoom}%")
        # self.statusbar.memory_label.setText(helper.get_memory_usage())
        self.set_title(self.curr_img.get_file_name_only())
        if self.curr_img.image_state == ImageProperty.IMAGE_STATE_PROBLEM:
            self.statusbar.flash_message(red("problem"))

    def closeEvent(self, event):
        self.settings.write()

# end class Window(QMainWindow)


def check_api_keys():
    if not cfg.TUMBLR_API_KEY:
        log.warning("missing environment variable: TUMBLR_API_KEY")
        log.warning("without this we cannot process tumblr posts")
        log.warning("acquire a tumblr API key (free) and set it as an env. variable")
        log.info(cfg.SEPARATOR)
    else:
        log.info("tumblr API key was found")

    if not cfg.IMGUR_CLIENT_ID or not cfg.IMGUR_CLIENT_SECRET:
        log.warning("missing environment variables: IMGUR_CLIENT_ID and/or IMGUR_CLIENT_SECRET")
        log.warning("without them we cannot process imgur albums / galleries")
        log.warning("acquire an imgur API key (free) and set them as env. variables")
        log.info(cfg.SEPARATOR)
    else:
        log.info("imgur API keys were found")


def main():
    App = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec())

##############################################################################

if __name__ == "__main__":
    check_api_keys()
    main()