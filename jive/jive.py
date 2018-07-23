#!/usr/bin/env python3

"""
This is the main file.
"""

try:
    # check compatibility
    eval('f"{1+1}"')
except SyntaxError:
    raise ImportError("The application requires Python 3.6+")

##############################################################################

if __name__ == "__main__":
    import os, sys
    # This is a trick. This way I can launch jive.py (this file) during
    # the development and I don't need to start ../start.py every time.
    folder: str = os.path.join(os.path.dirname(__file__), "..")
    if folder not in sys.path:
        sys.path.insert(0, folder)
    sys.argv[0] = "../start.py"
# endif

##############################################################################

import sys

import os
import random
import requests
from PyQt5 import QtGui
from PyQt5 import sip
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QCursor, QKeySequence, QPixmap
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import (QAction, QApplication, QDesktopWidget,
                             QFileDialog, QFrame, QInputDialog, QLabel,
                             QLineEdit, QMainWindow, QMenu, QMessageBox,
                             QScrollArea, QShortcut, QVBoxLayout, qApp)
from functools import partial
from pathlib import Path

from jive import autodetect
from jive import cache
from jive import categories
from jive import config as cfg
from jive import duplicates
from jive import fileops
from jive import help_dialogs
from jive import helper
from jive import mylogging as log
from jive import opener
from jive import settings
from jive import shortcuts as scuts
from jive import statusbar as sbar
from jive.commit import Commit
from jive.customurls import CustomUrls
from jive.exceptions import ImageError, FileNotSaved
from jive.extractors import imgur, subreddit, tumblr, sequence
from jive.helper import bold, gray, green, lightblue, pretty_num, red, yellow, blue
from jive.imageinfo import ImageInfo
from jive.imageview import ImageView
from jive.imagewithextra import ImageWithExtraInfo
from jive.important import ImportantFilesAndFolders
from jive.simplescrape import SimpleScrape
from jive.urlfolding import UrlFolding

OFF: bool = False
ON: bool = True

# Leave it here! This way we force pyinstaller to include PyQt5.sip.so
# in the EXE. Without that file the EXE fails to start and for some reason
# it was not added automatically.
sip_version: int = sip.SIP_VERSION

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

#########################
#                       #
#  class ImageProperty  #
#                       #
#########################

class ImageProperty:
    """
    Properties of the current (previous / next) image(s).
    """
    IMAGE_STATE_OK = 1
    IMAGE_STATE_PROBLEM = 2

    def __init__(self, img, parent):
        if isinstance(img, ImageWithExtraInfo):
            self.name = img.fpath_or_url
            self.extra_info = img.extra_info
        else:
            self.name = img
            self.extra_info = {}
        self.local_file = self._is_local_file(self.name)
        self.parent = parent
        self.zoom_ratio = 1.0
        self.original_img = None    # will be set in read()
        self.image_state = None     # will be set in read()
        self.zoomed_img = None      # will be set in read()
        self.file_size = -1         # will be set in read()
        self.to_save = False
        self.to_delete = False
        self.to_wallpaper = False

    @classmethod
    def to_pixmap(cls, name, cache):
        try:
            pm = None
            file_size = -1
            if os.path.isfile(name):
                pm = QPixmap(name)
                file_size = os.path.getsize(name)
            else:
                if name.startswith(("http://", "https://")):
                    url = name
                    if cache.enabled() and url in cache:
                        # log.debug(f"cache news: {url} was found in the cache :)")
                        fname = cache.get_fname_to_url(url)
                        # log.debug(f"fname: {fname}")
                        pm = QPixmap(fname)
                        file_size = os.path.getsize(fname)
                    else:

                        r = requests.get(url, headers=cfg.headers, timeout=cfg.REQUESTS_TIMEOUT)
                        if r.status_code == 403:    # forbidden
                            # log.debug("status code: 403")
                            referer = helper.get_referer(url)
                            copy = cfg.headers.copy()
                            copy.update({'referer': referer})
                            r = requests.get(url, headers=copy, timeout=cfg.REQUESTS_TIMEOUT)
                        data = r.content
                        pm = QPixmap()
                        pm.loadFromData(data)
                        try:
                            file_size = int(r.headers['Content-Length'])
                        except KeyError:
                            pass    # file_size remains -1
                        if cache.enabled():
                            cache.save(url, data)
            #
            if pm is None or pm.width() == 0:
                raise ImageError
            # else
            return (pm, cls.IMAGE_STATE_OK, file_size)
        except:
            log.warning(f"cannot read the image {name}")
            return (QPixmap(str(Path(cfg.ASSETS_DIR, "not_found.png"))), cls.IMAGE_STATE_PROBLEM, -1)

    def read(self, force=False, preload=False):
        """
        Construct the pixmap for the current image.

        Preload: read the original image but don't construct yet the zoomed image.
        Idea: we show the current image and preload the next one. Here the user may
        resize the window. Then (s)he goes to the next image, which was preloaded. On it,
        we call read() again, which will construct the zoomed image but it won't read
        the original image again.

        If the image has already been read, then there's nothing to do (we don't read it again).
        If `force` is True, then the images are re-read.
        """
        if force:
            self.free()

        if self.original_img is None:
            self.original_img, self.image_state, self.file_size = self.to_pixmap(self.name, self.parent.cache)

        if preload == False:
            self.zoomed_img = self.calculate_zoomed_image()

        # if preload:
        #     log.debug(f"the image {self.name} was preloaded")

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
        return self.zoomed_img

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

    def get_file_size(self, human_readable=False):
        if not human_readable:
            return self.file_size
        else:
            return helper.file_size_fmt(self.file_size) if self.file_size > -1 else ""

    def toggle_save(self):
        self.to_save = not self.to_save

    def toggle_delete(self):
        self.to_delete = not self.to_delete

    def toggle_wallpaper(self):
        self.to_wallpaper = not self.to_wallpaper

    def set_file_size(self):
        self.file_size = os.path.getsize(self.name)

    def get_flags(self):
        sb = []
        if self.to_save:
            sb.append("save")
        if self.to_delete:
            sb.append("delete")
        if self.to_wallpaper:
            sb.append("wallpaper")
        return ", ".join(sb) if sb else "--"

    def get_short_flags(self):
        sb = []
        if self.to_save:
            sb.append(yellow("S"))
        if self.to_delete:
            sb.append(red("D"))
        if self.to_wallpaper:
            sb.append(lightblue("W"))
        return "<br>".join(sb)

    def is_it_in_a_subreddit(self):
        """
        If this image is in a subreddit, return True.
        Else, return False.
        """
        return "subreddit" in self.extra_info

    def is_it_really_the_last(self):
        """
        Return True if this image is really the last and there is no way to load more images.
        For instance: we open a folder.

        At the moment there is only one possibility to load more images: when we open a subreddit.
        So, if we are in a subreddit, False is returned.
        """
        if self.is_it_in_a_subreddit():
            return False

        return True

    def save_to_filesystem(self, folder, method):
        """
        Save the image to the given folder.

        Return True if saving was successful. False, otherwise.
        """
        try:
            res = fileops.save(self, folder, self.parent.cache)
            # if save was successful:
            if res:
                if method == cfg.WALLPAPER_SAVE:
                    self.toggle_wallpaper()
                if method == cfg.NORMAL_SAVE:
                    self.toggle_save()
                return True
            else:
                raise FileNotSaved
        except requests.exceptions.Timeout:
            log.warning(f"timeout exception happened with {self.get_absolute_path_or_url()}")
        except FileNotSaved:
            log.warning(f"couldn't save {self.get_absolute_path_or_url()} to {folder}")
        except:
            log.warning(f"unknown exception happened while saving {self.get_absolute_path_or_url()} to {folder}")
        #
        return False

    def save_as(self, dest):
        """
        Save the image to dest (where dest is the absolute path of the destination).

        Return True if saving was successful. False, otherwise.
        """
        try:
            res = fileops.save_as(self, self.parent.cache, dest)
            # if save was successful:
            if res:
                return True
            else:
                raise FileNotSaved
        except requests.exceptions.Timeout:
            log.warning(f"timeout exception happened with {self.get_absolute_path_or_url()}")
        except FileNotSaved:
            log.warning(f"couldn't save {self.get_absolute_path_or_url()} as {dest}")
        except:
            log.warning(f"unknown exception happened while saving {self.get_absolute_path_or_url()} as {dest}")
        #
        return False
# end class ImageProperty


#####################
#                   #
#  class ImageList  #
#                   #
#####################

class ImageList:
    def __init__(self, parent):
        self.mainWindow = parent
        self.reset()

        self._prev_random_img_idx = -1

    def reset(self):
        self._list_of_images = []
        self._curr_img_idx = -1
        self._curr_img = None

    def get_curr_img(self):
        return self._curr_img

    def set_curr_img(self, img):
        self._curr_img = img

    def get_curr_img_idx(self):
        return self._curr_img_idx

    def set_curr_img_idx(self, idx):
        self._curr_img_idx = idx

    def get_list_of_images(self):
        return self._list_of_images

    def set_list_of_images(self, lst):
        self._list_of_images = lst

    def _find_image_index_by_name(self, name):
        for i in range(len(self._list_of_images)):
            if self._list_of_images[i].name == name:
                return i
            #
        #
        return -1    # not found

    def shuffle_images(self):
        # if there are no images or if there is only one, shuffle makes no sense
        length = len(self._list_of_images)
        if (length == 0) or (length == 1):
            self.mainWindow.statusbar.flash_message(blue("done"))
            return
        # else
        name = self._curr_img.name
        old_name = self._curr_img.name
        # Make sure that we position on a different image
        # every time we make a shuffle. Retry 10 times to
        # avoid an infinite loop.
        for i in range(10):
            random.shuffle(self._list_of_images)
            new_name = self._list_of_images[0].name
            if new_name != old_name:
                break
            #
        #
        new_idx = self._find_image_index_by_name(name)
        self._curr_img_idx = new_idx
        #
        self.mainWindow.statusbar.flash_message(blue("done"))
        self.jump_to_image(0)    # it will free the current image if necessary

    def jump_to_next_image(self):
        if len(self._list_of_images) == 0:
            self.mainWindow.statusbar.flash_message(red("no more"), wait=cfg.MESSAGE_FLASH_TIME_1)
            self.mainWindow.play_error_sound()
            return
        # else
        if self._curr_img_idx == len(self._list_of_images) - 1:
            self.mainWindow.statusbar.flash_message(red("no more"), wait=cfg.MESSAGE_FLASH_TIME_1)
            if self._curr_img.is_it_really_the_last():
                self.mainWindow.play_error_sound()
            img = self._curr_img
            subreddit_name = img.extra_info.get("subreddit")
            after_id = img.extra_info.get("after_id")
            if img and subreddit_name and after_id:
                urls = []
                if self.mainWindow.auto_load_next_subreddit_page:
                    urls = subreddit.read_subreddit(subreddit_name,
                                                    after_id,
                                                    statusbar=self.mainWindow.statusbar,
                                                    mainWindow=self.mainWindow)
                else:
                    reply = QMessageBox.question(self.mainWindow,
                                                 'Question',
                                                 "Load the next page?",
                                                 QMessageBox.Yes | QMessageBox.No,
                                                 QMessageBox.Yes)

                    if reply == QMessageBox.No:
                        return
                    else:
                        # self.open_subreddit(subreddit, after_id)
                        urls = subreddit.read_subreddit(subreddit_name,
                                                        after_id,
                                                        statusbar=self.mainWindow.statusbar,
                                                        mainWindow=self.mainWindow)

                if len(urls) == 0:
                    QMessageBox.information(self,
                                            "Info",
                                            "No new images were found.")
                else:
                    lst = [ImageProperty(url, self.mainWindow) for url in urls]
                    self._list_of_images.extend(lst)
                    self.jump_to_next_image()
                return
            else:
                return
        # else
        new_idx = self._curr_img_idx + 1
        if new_idx >= len(self._list_of_images):
            new_idx = len(self._list_of_images) - 1
        #
        self.jump_to_image(new_idx)

    def jump_to_first_image(self):
        self.jump_to_image(0)

    def jump_to_last_image(self):
        new_idx = len(self._list_of_images) - 1
        self.jump_to_image(new_idx)

    def jump_to_prev_image(self):
        if len(self._list_of_images) == 0 or self._curr_img_idx == 0:
            self.mainWindow.statusbar.flash_message(red("no less"), wait=cfg.MESSAGE_FLASH_TIME_1)
            self.mainWindow.play_error_sound()
            return
        # else
        new_idx = self._curr_img_idx - 1
        if new_idx < 0:
            new_idx = 0
        #
        self.jump_to_image(new_idx)

    def jump_five_percent_forward(self):
        offset = round(5 * len(self._list_of_images) / 100)
        self.jump_to_image(self._curr_img_idx + offset)

    def jump_five_percent_backward(self):
        offset = round(5 * len(self._list_of_images) / 100)
        self.jump_to_image(self._curr_img_idx - offset)

    def jump_to_image(self, new_idx):
        old_idx = self._curr_img_idx
        if old_idx == new_idx:
            return
        self._curr_img_idx = new_idx
        #
        if self._curr_img_idx >= len(self._list_of_images):
            self._curr_img_idx = len(self._list_of_images) - 1
        if self._curr_img_idx < 0:
            self._curr_img_idx = 0
        #
        self._curr_img = self._list_of_images[self._curr_img_idx].read()
        # not needed any more, free_others() will take care of it
        # if old_idx >= 0 and old_idx != self.imgList.curr_img_idx:
        #     self.imgList.list_of_images[old_idx].free()  # don't forget to free it!
        self.mainWindow.scroll_to_top()
        self.mainWindow.redraw()
        #
        if self.mainWindow.preload:
            self.preload_next_image()
            self.preload_prev_image()

        # let's always call it (with and without preload), just to be sure to free memory
        self.free_others()

        # log.debug(self.imgList.curr_img.extra_info)

    def jump_to_image_and_dont_care_about_the_previous_image(self, idx):
        self._curr_img_idx = idx
        #
        if self._curr_img_idx >= len(self._list_of_images):
            self._curr_img_idx = len(self._list_of_images) - 1
        if self._curr_img_idx < 0:
            self._curr_img_idx = 0
        #
        self._curr_img = self._list_of_images[self._curr_img_idx].read()
        self.mainWindow.scroll_to_top()
        self.mainWindow.redraw()
        #
        if self.mainWindow.preload:
            self.preload_next_image()
            self.preload_prev_image()

        # let's always call it (with and without preload), just to be sure to free memory
        self.free_others()

    def preload_next_image(self):
        try:
            next_img = self._list_of_images[self._curr_img_idx + 1]
            next_img.read(preload=True)
        except IndexError:
            pass    # we are at the last image, there's no next one

    def preload_prev_image(self):
        try:
            minus_1 = self._curr_img_idx - 1
            if minus_1 < 0:
                raise IndexError
            prev_img = self._list_of_images[minus_1]
            prev_img.read(preload=True)
        except IndexError:
            pass    # we are at the beginning, there's no previous one

    def free_others(self):
        """
        Without preload, browsing worked like this: you are on an image (A),
        and you jump to somewhere (new). You load the new image and you free the
        resources of old image A to avoid filling the memory with large QPixmap objects.

        Preload works like this: you jump somewhere (A). You load the image A and you preload
        the image that comes after A. If you go forward, it's OK. Say you are at image A and A+1 is preloaded.
        However, if you go backward, the resources of A+1 are not freed. That's a problem.

        Idea: you jump to image A, load it, and preload A+1. Then go over the list and free
        the resources of all the other images, except A and A+1.

        New: we also keep the previous image. That is, we keep 3 images: previous, current, next.
        With the exception of these three, free all the others.
        """
        plus_1 = self._curr_img_idx + 1
        if plus_1 >= len(self._list_of_images):
            plus_1 = self._curr_img_idx
        #
        minus_1 = self._curr_img_idx - 1
        if minus_1 < 0:
            minus_1 = 0

        before = self._list_of_images[:minus_1]
        after = self._list_of_images[plus_1 + 1:]
        others = before + after
        for img in others:
            img.free()
        # log.debug(f"{len(others)} images were freed")

    def jump_to_random_image(self):
        if len(self._list_of_images) > 1:
            # always choose a different image:
            while True:
                idx = random.randrange(len(self._list_of_images))
                if idx != self._curr_img_idx:
                    break
                #
            #
            self._prev_random_img_idx = self._curr_img_idx    # save where we were
            self.jump_to_image(idx)

    def jump_to_prev_random_image(self):
        if self._prev_random_img_idx == -1:
            return
        # else
        jump_to = self._prev_random_img_idx
        self._prev_random_img_idx = self._curr_img_idx  # save where we were
        self.jump_to_image(jump_to)

    def to_save(self):
        """
        Number of images flagged to be saved.
        """
        return sum(1 for img in self._list_of_images if img.to_save)

    def to_delete(self):
        """
        Number of images flagged to be deleted.
        """
        return sum(1 for img in self._list_of_images if img.to_delete)

    def to_wallpaper(self):
        """
        Number of images flagged to be saved as wallpapers.
        """
        return sum(1 for img in self._list_of_images if img.to_wallpaper)

    def has_something_to_commit(self):
        val1 = self.to_save()
        val2 = self.to_delete()
        val3 = self.to_wallpaper()

        return any([val1, val2, val3])

    def mark_all_images_to_save(self):
        for img in self._list_of_images:
            img.to_save = True

    def get_image_list(self):
        """
        Return the path / URL of the images that are in the current list.
        """
        result = [img.get_absolute_path_or_url() for img in self._list_of_images]
        return result


######################
#                    #
#  class MainWindow  #
#                    #
######################

class MainWindow(QMainWindow):
    def __init__(self, argv):
        super().__init__()
        self.argv = argv

        # log.debug(f"argv: {argv}")

        self.title = "JiVE"
        self.top = 50
        self.left = 50
        self.width = 900
        self.height = 600

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

        self.imgList = ImageList(self)

        # self.list_of_images = []
        # self.curr_img_idx = -1
        # self.curr_img = None

        self.shortcuts = scuts.Shortcuts()
        self.add_shortcuts()

        self.image_info_dialog = None                     # will be set later
        self.important_files_and_folders_dialog = None    # will be set later

        self.init_ui()

        self.commit = Commit(self)    # it must come after the init_ui()

        self.cache = cache.Cache(cfg.PREFERENCES_OPTIONS, cfg.PLATFORM_SETTINGS["cache_dir"])

        self.preload = True if cfg.PREFERENCES_OPTIONS.get("preload", "") == "yes" else False

        self.use_audio = True if cfg.PREFERENCES_OPTIONS.get("use_audio", "") == "yes" else False
        if self.use_audio:
            self.error_sound = QSound(cfg.ERROR_SOUND, self)

        self.auto_load_next_subreddit_page = \
            True if cfg.PREFERENCES_OPTIONS.get("auto_load_next_subreddit_page", "") == "yes" else False

        self.toggle_auto_fit()           # set it ON and show the flash message
        self.toggle_show_image_path()    # make it False and hide it

        self.reset()    # it must be last thing here

        if len(self.argv) > 1:
            self.process_arguments(self.argv)

        # These are here after reset() just for testing.
        # TO BE REMOVED in the release version.
        # self.open_local_dir(TEST_DIR)
        # self.open_subreddit(TEST_SUBREDDIT)
        # self.open_imgur_album(TEST_IMGUR_ALBUM)
        # self.open_remote_url_file(TEST_REMOTE_URL_FILE)
        # self.open_tumblr_post(TEST_TUMBLR_POST)

    def reset(self, msg=None):
        self.setWindowTitle(self.title)

        self.imgList.reset()

        # self.imgList.list_of_images = []
        # self.imgList.curr_img_idx = -1
        # self.imgList.curr_img = None

        if self.imgList.get_curr_img() is None:
            self.show_logo()

        self.info_line.setText("")
        self.statusbar.reset()
        if msg:
            self.statusbar.flash_message(msg)
        #
        # if the categories.yaml was changed
        self.create_contextmenu()
        # remove on-screen flags (S, D, W):
        self.flags_line.setText("")

    def process_arguments(self, argv):
        param = argv[1]
        self.auto_detect(param)

    def auto_detect(self, text):
        # log.debug(f"param: {text}")

        # try to open it as a local file / dir.
        res = self.open_local_file_or_dir(text)
        if res:
            return
        # else, try to open it as a remote URL / subreddit / etc.
        self.auto_detect_and_open(text, called_from_gui=False)

    # def mouseMoveEvent(self, event):    # doesn't work :( I wanted to monitor the cursor position
    #     p = event.pos()
    #     x, y = p.x(), p.y()
    #     print(f"x: {x}, y: {y}")

    def mousePressEvent(self, event):
        """
        If you left click on the left 25% (by width), go to the previous image.
        If you left click on the right 25% (by width), go to the next image.

        Only left click is accepted for this kind of browsing.
        """
        if event.button() != Qt.LeftButton:
            return
        # else
        p = event.pos()
        x, y = p.x(), p.y()
        # print(x, y)
        width = self.img_view.width()
        if x < width * (1 / 4):
            self.imgList.jump_to_prev_image()
            # print("prev")
        if x > width * (3 / 4):
            self.imgList.jump_to_next_image()
            # print("next")

    def wheelEvent(self, event):
        p = event.angleDelta()
        x, y = p.x(), p.y()
        offset = 75
        if y < 0:
            self.scroll_down(offset)
        else:
            self.scroll_up(offset)

    def set_title(self, prefix=""):
        if prefix:
            self.setWindowTitle(f"{prefix} - {self.title}")

    def open_local_dir(self, local_folder, redraw=False):
        self.imgList.set_list_of_images(self.read_local_dir(local_folder))
        if len(self.imgList.get_list_of_images()) == 0:
            log.warning("no images were found")
            return
        # else
        self.imgList.set_curr_img_idx(-1)
        self.imgList.jump_to_image(0)  # this way the 2nd image will be preloaded
        # self.imgList.curr_img_idx = 0
        # self.imgList.curr_img = self.imgList.list_of_images[0].read()
        #
        if redraw:
            self.redraw()

    def open_local_file(self, local_file, redraw=False):
        self.imgList.set_list_of_images(self.read_local_dir(str(Path(local_file).parent)))
        if len(self.imgList.get_list_of_images()) == 0:
            log.warning("no images were found")
            return
        # else
        jump_here = 0
        for i in range(len(self.imgList.get_list_of_images())):
            if self.imgList.get_list_of_images()[i].name == local_file:
                jump_here = i
                break
        self.imgList.set_curr_img_idx(-1)
        self.imgList.jump_to_image(jump_here)
        # self.imgList.curr_img = self.imgList.list_of_images[self.imgList.curr_img_idx].read()
        #
        if redraw:
            self.redraw()

    def open_local_file_or_dir(self, name):
        """
        Returns True if it was a local file or a local directory.
        Otherwise, it returns False.
        """
        p = Path(name)
        # log.debug(p.absolute())
        if p.is_file():
            self.open_local_file(str(p), redraw=True)
            return True
        if p.is_dir():
            self.open_local_dir(str(p), redraw=True)
            return True
        #
        return False

    def open_remote_url_file(self, url):
        if Path(url).suffix.lower() not in cfg.SUPPORTED_FORMATS:
            log.warning("unsupported file format")
            return
        # else
        self.imgList.set_list_of_images([ImageProperty(url, self)])
        self.imgList.set_curr_img_idx(0)
        self.imgList.set_curr_img(self.imgList.get_list_of_images()[0].read())

    def open_subreddit(self, text, after_id=None):
        subreddit_name = subreddit.get_subreddit_name(text)
        if not subreddit_name:
            log.warning("that's not a subreddit")
            return
        # else
        urls = subreddit.read_subreddit(subreddit_name, after_id, statusbar=self.statusbar, mainWindow=self)
        self.open_urls(urls)

    def open_urls(self, urls):
        if len(urls) == 0:
            log.warning("no images could be extracted")
            self.statusbar.flash_message(red("no images found"))
            return
        # else
        self.imgList.set_list_of_images([ImageProperty(url, self) for url in urls])
        self.imgList.set_curr_img_idx(-1)   # refresh the first image if we are there
        self.imgList.jump_to_image(0)    # this way the 2nd image will be preloaded

    def open_sequence_urls(self, seq_url, redraw=False):
        urls = sequence.get_urls_from_sequence_url(seq_url)
        self.open_urls(urls)

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
        self.imgList.set_list_of_images([ImageProperty(url, self) for url in urls])
        if len(self.imgList.get_list_of_images()) > 0:
            self.imgList.set_curr_img_idx(0)
            self.imgList.set_curr_img(self.imgList.get_list_of_images()[0].read())

    def open_tumblr_post(self, text):
        url = text
        if not tumblr.is_post(url):
            log.warning("that's not a tumblr post")
            return

        urls = tumblr.extract_images_from_a_specific_post(url)
        self.open_urls(urls)

    def play_error_sound(self):
        if self.use_audio:
            self.error_sound.play()

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

        self.loading_line = QLabel(self.img_view)
        self.loading_line.setText(green("Loading...", bold=True))
        default_font_name = QtGui.QFont().defaultFamily()
        new_font = QtGui.QFont(default_font_name, 15)
        self.loading_line.setFont(new_font)
        self.loading_line.setMinimumWidth(cfg.LONG)
        self.loading_line.setMinimumHeight(cfg.LONG)
        self.loading_line.setAlignment(Qt.AlignTop)
        self.loading_line.hide()

        self.flags_line = QLabel(self.img_view)
        default_font_name = QtGui.QFont().defaultFamily()
        new_font = QtGui.QFont(default_font_name, 30)
        self.flags_line.setFont(new_font)
        self.flags_line.setMinimumWidth(cfg.LONG)
        self.flags_line.setMinimumHeight(cfg.LONG)
        self.flags_line.setAlignment(Qt.AlignTop)
        self.flags_line.move(20, 60)
        self.flags_line.show()

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
        text, okPressed = QInputDialog.getText(self,
                                               "Open subreddit",
                                               "Subreddit's name or its URL:" + " " * 50,
                                               QLineEdit.Normal,
                                               "")
        text = text.strip()
        if okPressed and text:
            what = autodetect.detect(text)
            kind = what[0] if what else None
            if kind in (autodetect.AutoDetectEnum.subreddit_url,
                        autodetect.AutoDetectEnum.subreddit_name,
                        autodetect.AutoDetectEnum.subreddit_r_name):
                self.open_subreddit(text)
            else:
                log.warning("that's not a subreddit")
                self.statusbar.flash_message(red("not a subreddit"))
                self.play_error_sound()

    def menu_open_imgur_album(self):
        text, okPressed = QInputDialog.getText(self,
                                               "Open Imgur album",
                                               "Complete URL:" + " " * 80,
                                               QLineEdit.Normal,
                                               "")
        text = text.strip()
        if okPressed and text:
            what = autodetect.detect(text)
            kind = what[0] if what else None
            if kind:
                if kind == autodetect.AutoDetectEnum.imgur_album:
                    self.open_imgur_album(text)
                    self.redraw()
                if kind == autodetect.AutoDetectEnum.imgur_html_page_with_embedded_image:
                    img = what[1]
                    log.info("it seems to be an imgur HTML page with an embedded image")
                    self.open_remote_url_file(img)
                    self.redraw()
            else:
                log.warning("that's not an imgur album / gallery / HTML")
                self.statusbar.flash_message(red("not an imgur link"))
                self.play_error_sound()

    def menu_open_url_auto_detect(self):
        text, okPressed = QInputDialog.getText(self,
                                               "Auto detect URL",
                                               "URL / subreddit / etc.:" + " " * 80,
                                               QLineEdit.Normal,
                                               self.settings.get_last_open_url_auto_detect())
        text = text.strip()
        if okPressed and text:
            self.auto_detect_and_open(text)

    def auto_detect_and_open(self, text, called_from_gui=True):
        if called_from_gui:
            self.settings.set_last_open_url_auto_detect(text)

        what = autodetect.detect(text)
        if what is None:
            log.warning("hmm, it seems to be something new...")
            return

        # else, if it was detected
        kind = what[0]    # since "type" is a keyword
        if kind == autodetect.AutoDetectEnum.image_url:
            log.info("it seems to be a remote image")
            self.open_remote_url_file(text)
            self.redraw()
            return
        if kind in (autodetect.AutoDetectEnum.subreddit_url,
                    autodetect.AutoDetectEnum.subreddit_name,
                    autodetect.AutoDetectEnum.subreddit_r_name):
            log.info("it seems to be a subreddit")
            self.open_subreddit(text)
            return
        if kind == autodetect.AutoDetectEnum.imgur_album:
            log.info("it seems to be an Imgur album")
            self.open_imgur_album(text)
            self.redraw()
            return
        if kind == autodetect.AutoDetectEnum.tumblr_post:
            log.info("it seems to be a Tumblr post")
            self.open_tumblr_post(text)
            self.redraw()
            return
        if kind == autodetect.AutoDetectEnum.sequence_url:
            log.info("it seems to be a sequence URL")
            self.open_sequence_urls(text)
            return
        if kind == autodetect.AutoDetectEnum.imgur_html_page_with_embedded_image:
            img = what[1]
            log.info("it seems to be an imgur HTML page with an embedded image")
            self.open_remote_url_file(img)
            self.redraw()
            return

        log.info("it was detected but it was not handled...")

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
        self.open_url_open_imgur_album_act = QAction("Open &Imgur album / gallery / HTML", self)
        self.open_url_open_imgur_album_act.triggered.connect(self.menu_open_imgur_album)
        #
        key = "Ctrl+S"
        self.save_image_act = QAction("&Save current image as...", self)
        self.shortcuts.register_menubar_action(key, self.save_image_act, self.save_image)
        #
        self.save_image_list_act = QAction("Save image list as...", self)
        self.save_image_list_act.triggered.connect(self.save_image_list)
        #
        self.export_image_list_to_clipboard_act = QAction("E&xport image list to clipboard", self)
        self.export_image_list_to_clipboard_act.triggered.connect(self.export_image_list_to_clipboard)
        #
        key = "F5"
        self.reload_current_image_act = QAction("&Reload current image", self)
        self.shortcuts.register_menubar_action(key, self.reload_current_image_act, self.reload_current_image)
        #
        key = "I"
        self.image_info_act = QAction("Image &info", self)
        self.shortcuts.register_menubar_action(key, self.image_info_act, self.image_info)
        # self.image_info_act = QAction("Image info", self)
        # self.image_info_act.triggered.connect(self.image_info)
        #
        self.slideshow_act = QAction("Slideshow", self)
        self.slideshow_act.triggered.connect(self.slideshow)
        #
        self.important_files_and_folders_act = QAction("Important &files and folders", self)
        self.important_files_and_folders_act.triggered.connect(self.important_files_and_folders)
        #
        self.help_act = QAction("&Help", self)
        self.help_act.triggered.connect(help_dialogs.open_help)
        #
        self.about_act = QAction("&About", self)
        self.about_act.triggered.connect(partial(help_dialogs.open_about, self))
        #
        self.about_qt_act = QAction("About &Qt", self)
        self.about_qt_act.triggered.connect(qApp.aboutQt)
        #
        key = "Ctrl+Alt+R"
        self.reset_act = QAction("Reset", self)
        self.shortcuts.register_menubar_action(key, self.reset_act, partial(self.reset, "reset"))
        #
        key = "Q"
        self.quit_act = QAction("&Quit", self)
        self.shortcuts.register_menubar_action(key, self.quit_act, self.close)
        #
        key = "I"
        self.image_info_act = QAction("Image &info", self)
        self.shortcuts.register_menubar_action(key, self.image_info_act, self.image_info)
        #
        key = "Alt+M"
        self.hide_menubar_act = QAction("&Hide menu bar", self)
        self.shortcuts.register_menubar_action(key, self.hide_menubar_act, self.toggle_menubar)
        #
        key = "Ctrl+M"
        self.show_mouse_pointer_act = QAction("Show &mouse pointer", self, checkable=True, checked=True)
        self.shortcuts.register_menubar_action(key, self.show_mouse_pointer_act, self.toggle_mouse_pointer)
        #
        self.shuffle_images_act = QAction("&Shuffle images", self)
        self.shuffle_images_act.triggered.connect(self.imgList.shuffle_images)
        #
        self.open_with_gimp_act = QAction("&Gimp", self)
        self.open_with_gimp_act.triggered.connect(self.open_with_gimp)
        #
        self.find_duplicates_act = QAction("Find &duplicates", self)
        self.find_duplicates_act.triggered.connect(self.find_duplicates)
        #
        self.sequence_urls_act = QAction("Open se&quence URL", self)
        self.sequence_urls_act.triggered.connect(self.sequence_urls)
        #
        self.image_url_act = QAction("Open image URL", self)
        self.image_url_act.triggered.connect(self.image_url)
        #
        self.open_url_open_tumblr_post_act = QAction("Open &Tumblr post", self)
        self.open_url_open_tumblr_post_act.triggered.connect(self.menu_open_tumblr_post)
        #
        key = "Ctrl+Shift+U"
        self.extract_images_from_webpage_act = QAction("E&xtract images from a webpage", self)
        self.shortcuts.register_menubar_action(key, self.extract_images_from_webpage_act, self.extract_images_from_webpage)
        #
        self.open_custom_url_list_act = QAction("Open &list of image URLs", self)
        self.open_custom_url_list_act.triggered.connect(self.open_custom_url_list)
        #
        self.url_folding_act = QAction("URL &folding / unfolding", self)
        self.url_folding_act.triggered.connect(self.url_folding)

    def create_menubar(self):
        self.menubar = self.menuBar()
        self.shortcuts.disable_conflicting_window_shortcuts()
        # self.menubar.setStyleSheet(cfg.TOP_AND_BOTTOM_BAR_STYLESHEET)

        open_url_acts = [self.open_url_auto_detect_act,
                         cfg.SEPARATOR,
                         self.image_url_act,
                         self.open_url_open_subreddit_act,
                         self.open_url_open_imgur_album_act,
                         self.open_url_open_tumblr_post_act,
                         self.sequence_urls_act]

        fileMenu = self.menubar.addMenu("&File")
        viewMenu = self.menubar.addMenu("&View")
        toolsMenu = self.menubar.addMenu("&Tools")
        helpMenu = self.menubar.addMenu("&Help")

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
        fileMenu.addAction(self.open_custom_url_list_act)
        fileMenu.addSeparator()
        fileMenu.addAction(self.save_image_act)
        fileMenu.addAction(self.save_image_list_act)
        fileMenu.addAction(self.export_image_list_to_clipboard_act)
        fileMenu.addAction(self.reload_current_image_act)
        fileMenu.addSeparator()
        fileMenu.addAction(self.reset_act)
        fileMenu.addAction(self.quit_act)

        # viewMenu
        viewMenu.addAction(self.image_info_act)
        viewMenu.addAction(self.important_files_and_folders_act)
        viewMenu.addSeparator()
        viewMenu.addAction(self.hide_menubar_act)
        viewMenu.addAction(self.show_mouse_pointer_act)

        # toolsMenu
        toolsMenu.addAction(self.shuffle_images_act)
        toolsMenu.addAction(self.find_duplicates_act)
        toolsMenu.addAction(self.extract_images_from_webpage_act)
        toolsMenu.addAction(self.url_folding_act)

        # helpMenu
        helpMenu.addAction(self.help_act)
        helpMenu.addAction(self.about_act)
        helpMenu.addAction(self.about_qt_act)
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
                         self.image_url_act,
                         self.open_url_open_subreddit_act,
                         self.open_url_open_imgur_album_act,
                         self.open_url_open_tumblr_post_act,
                         self.sequence_urls_act]

        open_with_acts = [self.open_with_gimp_act]

        # When I right-click, very often the first menu item gets selected.
        # "Nothing" is added to avoid that problem.
        nothing = "--"
        self.menu.addAction(QAction(nothing, self))
        self.menu.addSeparator()
        self.menu.addAction(self.open_file_act)
        self.menu.addAction(self.open_dir_act)
        open_url_menu = QMenu(self.menu)
        open_url_menu.setTitle("Open &URL...")
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
        self.menu.addSeparator()
        open_with_menu = QMenu(self.menu)
        open_with_menu.setTitle("Open with...")
        self.menu.addMenu(open_with_menu)
        self.menu.addAction(self.save_image_act)
        for entry in open_with_acts:
            if isinstance(entry, str):
                open_with_menu.addSeparator()
            else:
                open_with_menu.addAction(entry)
        self.menu.addSeparator()
        self.menu.addAction(self.image_info_act)
        self.menu.addAction(self.slideshow_act)
        self.menu.addSeparator()
        self.menu.addAction(self.quit_act)
        # When I right-click at the bottom of the screen, very often the last menu item gets selected.
        # "Nothing" is added to avoid an accidental quit.
        self.menu.addSeparator()
        self.menu.addAction(QAction(nothing, self))

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
        #
        key = "Ctrl+Q"
        self.shortcutCtrlQuit = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutCtrlQuit, self.close)

        key = "Ctrl+U"
        self.shortcutAutoDetect = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutAutoDetect, self.menu_open_url_auto_detect)

        key = "Z"
        self.shortcutFitWindowToImage = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutFitWindowToImage, self.toggle_fit_window_to_image)

        key = "F11"
        self.shortcutFullscreen = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutFullscreen, self.toggle_fullscreen)

        key = "Esc"
        self.shortcutFromFullscreenToNormal = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutFromFullscreenToNormal, self.from_fullscreen_to_normal)

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
        # "W" will rather be used to mark an image to be saved as a wallpaper
        # key = "W"
        # self.shortcutFitImageToWindowWidth = QShortcut(QKeySequence(key), self)
        # self.shortcuts.register_window_shortcut(key, self.shortcutFitImageToWindowWidth, self.fit_image_to_window_width)

        key = "Left"
        self.shortcutPrevImage = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutPrevImage, self.imgList.jump_to_prev_image)
        #
        key ="PgUp"
        self.shortcutNextImagePgUp = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutNextImagePgUp, self.imgList.jump_five_percent_backward)

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
        self.shortcuts.register_window_shortcut(key, self.shortcutNextImage, self.imgList.jump_to_next_image)
        #
        key = "PgDown"
        self.shortcutNextImagePgDn = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutNextImagePgDn, self.imgList.jump_five_percent_forward)

        key = "Home"
        self.shortcutFirstImage = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutFirstImage, self.imgList.jump_to_first_image)

        key = "End"
        self.shortcutLastImage = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutLastImage, self.imgList.jump_to_last_image)

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
        self.shortcuts.register_window_shortcut(key, self.shortcutJumpToRandomImg, self.imgList.jump_to_random_image)
        #
        key = "Shift+R"
        self.shortcutJumpToPrevRandomImg = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutJumpToPrevRandomImg, self.imgList.jump_to_prev_random_image)

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

        key = "I"
        self.shortcutImageInfo = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutImageInfo, self.image_info)

        key = "S"
        self.shortcutMarkToSave = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutMarkToSave, self.toggle_img_save)

        key = "D"
        self.shortcutMarkToDelete = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutMarkToDelete, self.toggle_img_delete)

        key = "W"
        self.shortcutMarkToWallpaper = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutMarkToWallpaper, self.toggle_img_wallpaper)

        key = "C"
        self.shortcutCommit = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutCommit, self.commit_changes)

        key = "Ctrl+A"
        self.shortcutMarkAllToSave = QShortcut(QKeySequence(key), self)
        self.shortcuts.register_window_shortcut(key, self.shortcutMarkAllToSave, self.mark_all_images_to_save)

    def mark_all_images_to_save(self):
        self.imgList.mark_all_images_to_save()
        self.statusbar.flash_message(blue("all marked for save"))
        self.redraw()

    def commit_changes(self):
        if not self.commit.has_something_to_commit():
            QMessageBox.information(self, "Info", "There's nothing to commit.")
            return
        # else, if there's something to commit
        to_del = self.commit.to_delete()
        remain = len(self.imgList.get_list_of_images()) - to_del
        msg = f"""
Do you want to commit your changes?

Save: {self.commit.to_save()}
Save as wallpaper: {self.commit.to_wallpaper()}
Delete: {to_del} (remain {remain})
""".strip()

        reply = QMessageBox.question(self,
                                     'Question',
                                     msg,
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.Yes)

        if reply == QMessageBox.No:
            return

        # else, if the user wants to commit the changes

        marked_to_wallpaper = self.commit.to_wallpaper()                # How many were marked?
        marked_to_wallpaper_success = self.commit.save_wallpapers()     # How many were saved successfully?
        w_ok = (marked_to_wallpaper == marked_to_wallpaper_success)     # OK, if the two values are identical

        marked_to_save = self.commit.to_save()
        marked_to_save_success = self.commit.save_others()
        s_ok = (marked_to_save == marked_to_save_success)

        marked_to_delete = self.commit.to_delete()
        marked_to_delete_success = self.commit.delete_files()
        d_ok = (marked_to_delete == marked_to_delete_success)

        ok = all([w_ok, s_ok, d_ok])            # OK, if everything was processed successfully
        popup = QMessageBox.information         # if OK, show an information popup
        if not ok:                              # otherwise show a warning popup
            popup = QMessageBox.warning

        self.redraw()    # hide flags on the screen if the flags were removed

        text = f"""
{marked_to_save_success} (of {marked_to_save}) images were saved
{marked_to_wallpaper_success} (of {marked_to_wallpaper}) images were saved as wallpapers
{marked_to_delete_success} (of {marked_to_delete}) images were deleted
""".strip()
        popup(self, "Commit summary", text)

    def toggle_img_save(self):
        if self.imgList.get_curr_img().image_state == ImageProperty.IMAGE_STATE_PROBLEM:
            self.statusbar.flash_message(red("no"))
            return
        # else
        if self.imgList.get_curr_img().local_file:
            msg = """
This is a <strong>local</strong> file.<br>
<br>
It makes no sense to mark it to be saved.
""".strip()
            QMessageBox.warning(self, "Warning", msg)
            return
        # else
        self.imgList.get_curr_img().toggle_save()
        if self.imgList.get_curr_img().to_save:
            self.statusbar.flash_message("+ save", cfg.MESSAGE_FLASH_TIME_1)
        else:
            self.statusbar.flash_message("- save", cfg.MESSAGE_FLASH_TIME_1)
        self.redraw()
        if self.imgList.get_curr_img().to_save:
            self.imgList.jump_to_next_image()

    def toggle_img_delete(self):
        if self.imgList.get_curr_img().image_state == ImageProperty.IMAGE_STATE_PROBLEM:
            self.statusbar.flash_message(red("no"))
            return
        # else
        if not self.imgList.get_curr_img().local_file:
            msg = """
This is a <strong>remote</strong> file with a URL.<br>
<br>
You cannot delete it.
""".strip()
            QMessageBox.warning(self, "Warning", msg)
            return
        # else
        self.imgList.get_curr_img().toggle_delete()
        if self.imgList.get_curr_img().to_delete:
            self.statusbar.flash_message("+ delete", cfg.MESSAGE_FLASH_TIME_1)
        else:
            self.statusbar.flash_message("- delete", cfg.MESSAGE_FLASH_TIME_1)
        self.redraw()
        if self.imgList.get_curr_img().to_delete:
            self.imgList.jump_to_next_image()

    def toggle_img_wallpaper(self):
        if self.imgList.get_curr_img().image_state == ImageProperty.IMAGE_STATE_PROBLEM:
            self.statusbar.flash_message(red("no"))
            return
        # else
        self.imgList.get_curr_img().toggle_wallpaper()
        if self.imgList.get_curr_img().to_wallpaper:
            self.statusbar.flash_message("+ wallpaper", cfg.MESSAGE_FLASH_TIME_1)
        else:
            self.statusbar.flash_message("- wallpaper", cfg.MESSAGE_FLASH_TIME_1)
        self.redraw()
        if self.imgList.get_curr_img().to_wallpaper:
            self.imgList.jump_to_next_image()

    def image_info(self):
        if not self.imgList.get_curr_img():
            self.statusbar.flash_message(red("no"))
            self.play_error_sound()
            return
        # else
        if self.imgList.get_curr_img().image_state == ImageProperty.IMAGE_STATE_PROBLEM:
            self.statusbar.flash_message(red("no"))
            return
        # else
        if self.image_info_dialog:
            self.image_info_dialog.close()    # allow just 1 instance; not needed if that window is modal
        self.image_info_dialog = ImageInfo(self, self.imgList.get_curr_img())

    def important_files_and_folders(self):
        if self.important_files_and_folders_dialog:
            self.important_files_and_folders_dialog.close()    # allow just 1 instance; not needed if that window is modal
        self.important_files_and_folders_dialog = ImportantFilesAndFolders(self)

    def slideshow(self):
        self.not_yet_implemented()

    def not_yet_implemented(self):
        self.statusbar.flash_message(red("not yet implemented"))

    def reload_current_image(self):
        if not self.imgList.get_curr_img():
            self.statusbar.flash_message(red("no"))
            self.play_error_sound()
            return
        # else
        self.statusbar.flash_message(blue("reload"))
        self.imgList.get_curr_img().read(force=True)
        self.redraw()

    def save_image(self):
        if not self.imgList.get_curr_img() or self.imgList.get_curr_img().image_state == ImageProperty.IMAGE_STATE_PROBLEM:
            self.statusbar.flash_message(red("no"))
            self.play_error_sound()
            return
        # else
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filter = "Images (*.bmp *.jpg *.jpe *.jpeg *.png *.pbm *.pgm *.ppm *.xbm *.xpm)"
        offer_fname = str(Path(self.settings.get_last_dir_save_as(), self.imgList.get_curr_img().get_file_name_only()))
        # print(offer_fname)
        file_obj = QFileDialog.getSaveFileName(self,
                                               caption="Save current image",
                                               directory=offer_fname,
                                               filter=filter,
                                               options=options)
        fname = file_obj[0]
        if fname:
            res = self.imgList.get_curr_img().save_as(fname)
            if res:
                log.info(f"the file was saved as {fname}")
                self.statusbar.flash_message(blue("saved"))
                self.settings.set_last_dir_save_as(str(Path(fname).parent))
            else:
                log.info(f"the file was NOT saved")

    def export_image_list_to_clipboard(self):
        lst = self.imgList.get_image_list()
        if len(lst) == 0:
            self.statusbar.flash_message(red("no"))
            self.play_error_sound()
            return
        # else
        content = ("\n".join(lst)).strip() + "\n"
        helper.copy_text_to_clipboard(content)
        log.info("the image list was copied to the clipboard")
        self.statusbar.flash_message(blue("copied to clipboard"))

    def save_image_list(self):
        lst = self.imgList.get_image_list()
        if len(lst) == 0:
            self.statusbar.flash_message(red("no"))
            self.play_error_sound()
            return
        # else
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        offer_fname = "image_list.txt"
        file_obj = QFileDialog.getSaveFileName(self,
                                               caption="Save image list",
                                               directory=offer_fname,
                                               options=options)
        fname = file_obj[0]
        if fname:
            content = "\n".join(lst)
            with open(fname, "w") as f:
                print(content, file=f)
            if Path(fname).is_file():
                log.info(f"image list was saved to {fname}")
                self.statusbar.flash_message(blue("saved"))

    def open_with_gimp(self):
        if not self.imgList.get_curr_img():
            self.statusbar.flash_message(red("no image"))
            return
        # else
        name = self.imgList.get_curr_img().get_absolute_path_or_url()
        opener.open_file_with_gimp(self, name)

    def find_duplicates(self):
        if len(self.imgList.get_list_of_images()) == 0:
            QMessageBox.information(self, "Info", "There are no duplicates.")
            return
        # else, there is at least 1 image
        if not self.imgList.get_curr_img().local_file:
            QMessageBox.information(self, "Info", "Finding duplicates works with <strong>local</strong> files only!")
            return
        # else, we only have local file(s)
        # find and mark duplicates
        cnt = duplicates.mark_duplicates(self.imgList.get_list_of_images())
        if cnt == 0:
            msg = "There are no duplicates."
        else:
            msg = f"""
{cnt} images were <strong>marked</strong> to be deleted.

If you want to delete them from the
file system, then <strong>commit</strong> your changes.
""".strip().replace("\n", "<br>")
        QMessageBox.information(self, "Info", msg)

    def sequence_urls(self):
        text, okPressed = QInputDialog.getText(self,
                                               "Sequence URL",
                                               "Sequence URL:" + " " * 80,
                                               QLineEdit.Normal,
                                               "")
        text = text.strip()
        if okPressed and text:
            what = autodetect.detect(text)
            kind = what[0] if what else None
            if kind == autodetect.AutoDetectEnum.sequence_url:
                self.open_sequence_urls(text)
            else:
                log.warning("that's not a sequence URL")
                self.statusbar.flash_message(red("not a sequence"))
                self.play_error_sound()

    def image_url(self):
        text, okPressed = QInputDialog.getText(self,
                                               "Image URL",
                                               "Image URL:" + " " * 80,
                                               QLineEdit.Normal,
                                               "")
        text = text.strip()
        if okPressed and text:
            what = autodetect.detect(text)
            kind = what[0] if what else None
            if kind == autodetect.AutoDetectEnum.image_url:
                self.open_remote_url_file(text)
                self.redraw()
            else:
                log.warning("that's not an image URL")
                self.statusbar.flash_message(red("not an image URL"))
                self.play_error_sound()

    def extract_images_from_webpage(self):
        self.simple_scrape = SimpleScrape(log)
        self.simple_scrape.show()
        self.simple_scrape.setFixedSize(self.simple_scrape.size())  # disable resize
        self.simple_scrape.urlList.connect(self.open_urls)

    def open_custom_url_list(self):
        self.custom_url_list = CustomUrls(log)
        self.custom_url_list.show()
        self.custom_url_list.setFixedSize(self.custom_url_list.size())  # disable resize
        self.custom_url_list.urlList.connect(self.open_urls)

    def url_folding(self):
        self.url_folding_window = UrlFolding()
        self.url_folding_window.show()
        self.url_folding_window.setFixedSize(self.url_folding_window.size())    # disable resize
        self.url_folding_window.urlList.connect(self.open_urls)

    def menu_open_tumblr_post(self):
        text, okPressed = QInputDialog.getText(self,
                                               "Open Tumblr post",
                                               "Complete URL:" + " " * 80,
                                               QLineEdit.Normal,
                                               "")
        text = text.strip()
        if okPressed and text:
            what = autodetect.detect(text)
            kind = what[0] if what else None
            if kind == autodetect.AutoDetectEnum.tumblr_post:
                self.open_tumblr_post(text)
                self.redraw()
            else:
                log.warning("that's not a tumblr post")
                self.statusbar.flash_message(red("not a tumblr post"))
                self.play_error_sound()

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
            self.hide_manubar()
        else:
            self.show_menubar()
        #
        self.redraw()

    def show_menubar(self):
        self.menubar.show()
        self.shortcuts.disable_conflicting_window_shortcuts()

    def hide_manubar(self):
        self.menubar.hide()
        self.statusbar.flash_message("Alt+M: show menu bar")
        self.shortcuts.enable_all_window_shortcuts()

    def dialog_go_to_image(self):
        total = len(self.imgList.get_list_of_images())
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
                self.imgList.jump_to_image(idx)
            except ValueError:
                self.statusbar.flash_message(red("invalid value"))

    def scroll_to_top(self):
        self.scroll.verticalScrollBar().setValue(0)

    def scroll_down(self, offset=100):
        val = self.scroll.verticalScrollBar().value()
        self.scroll.verticalScrollBar().setValue(val + offset)

    def scroll_right(self):
        val = self.scroll.horizontalScrollBar().value()
        self.scroll.horizontalScrollBar().setValue(val + 100)

    def scroll_up(self, offset=100):
        val = self.scroll.verticalScrollBar().value()
        self.scroll.verticalScrollBar().setValue(val - offset)

    def scroll_left(self):
        val = self.scroll.horizontalScrollBar().value()
        self.scroll.horizontalScrollBar().setValue(val - 100)

    def copy_path_to_clipboard(self):
        text = self.imgList.get_curr_img().get_absolute_path_or_url()
        helper.copy_text_to_clipboard(text)
        msg = "{0} copied to clipboard".format("path" if self.imgList.get_curr_img().local_file else "URL")
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
            self.hide_scrollbars()
        else:
            self.statusbar.mode_label.setText(gray("AUTO WIDTH OFF"))
            self.show_scrollbars()
        self.redraw()

    def zoom_in(self):
        if self.auto_fit or self.auto_width:
            self.statusbar.flash_message(red("oops, auto stuff is on"))
            return
        # else
        self.statusbar.flash_message("zoom in")
        self.imgList.get_curr_img().zoom_in()
        self.redraw()

    def zoom_out(self):
        if self.auto_fit or self.auto_width:
            self.statusbar.flash_message(red("oops, auto stuff is on"))
            return
        # else
        self.statusbar.flash_message("zoom out")
        self.imgList.get_curr_img().zoom_out()
        self.redraw()

    def zoom_reset(self):
        if self.auto_fit or self.auto_width:
            self.statusbar.flash_message(red("oops, auto stuff is on"))
            return
        # else
        self.statusbar.flash_message("reset zoom")
        self.imgList.get_curr_img().zoom_reset()
        self.redraw()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.statusBar().show()
            self.show_menubar()
        else:
            self.showFullScreen()
            self.statusBar().hide()
            self.hide_manubar()

    def from_fullscreen_to_normal(self):
        if self.isFullScreen():
            self.toggle_fullscreen()

    def toggle_fit_window_to_image(self):
        if self._fit_window_to_image_status == OFF:
            self._fit_window_to_image_width = self.geometry().width()
            self._fit_window_to_image_height = self.geometry().height()
            #
            self.resize(self.imgList.get_curr_img().zoomed_img.width(),
                        self.imgList.get_curr_img().zoomed_img.height())
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
        self.imgList.get_curr_img().fit_img_to_window()
        self.redraw()

    def fit_image_to_window_width(self):
        if self.auto_fit:
            self.statusbar.flash_message(red("oops, auto fit is on"))
            return
        # else
        self.statusbar.flash_message("fit width")
        self.imgList.get_curr_img().fit_img_to_window_width()
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
        pm = ImageProperty.to_pixmap(cfg.LOGO, self.cache)[0]
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
        if self.imgList.get_curr_img() is None:
            return
        #
        pm = self.imgList.get_curr_img().original_img.scaled(self.imgList.get_curr_img().zoom_ratio * self.geometry().width(),
                                               self.imgList.get_curr_img().zoom_ratio * self.geometry().height(),
                                               Qt.KeepAspectRatio,
                                               Qt.SmoothTransformation)
        # avoid upscale
        if pm.width() > self.imgList.get_curr_img().original_img.width() or pm.height() > self.imgList.get_curr_img().original_img.height():
            pm = self.imgList.get_curr_img().original_img
        self.imgList.get_curr_img().set_zoomed_img(pm)
        self.redraw()

    def redraw(self):
        # log.info("redraw")
        #
        if self.imgList.get_curr_img() is None:
            return
        #
        if self.auto_fit:
            self.imgList.get_curr_img().fit_img_to_window()
        if self.auto_width:
            self.imgList.get_curr_img().fit_img_to_window_width()
        pm = self.imgList.get_curr_img().zoomed_img
        self.image_label.setPixmap(pm)
        self.image_label.resize(pm.width(), pm.height())
        #
        resolution = "{w} x {h}".format(w=self.imgList.get_curr_img().original_img.width(), h=self.imgList.get_curr_img().original_img.height())
        # file_size = helper.file_size_fmt(self.imgList.curr_img.file_size) if self.imgList.curr_img.file_size > -1 else ""
        file_size_hr = self.imgList.get_curr_img().get_file_size(human_readable=True)
        zoom = int(self.imgList.get_curr_img().zoom_ratio * 100)
        #
        self.info_line.setText(green("{0} of {1}".format(pretty_num(self.imgList.get_curr_img_idx() + 1), pretty_num(len(self.imgList.get_list_of_images())))))
        #
        self.path_line.setText(green(self.imgList.get_curr_img().get_file_name_or_url()))
        #
        text = green(self.imgList.get_curr_img().get_short_flags())
        self.flags_line.setText(text)
        #
        self.statusbar.curr_pos_label.setText("{0} of {1}".format(pretty_num(self.imgList.get_curr_img_idx() + 1),
                                                                  pretty_num(len(self.imgList.get_list_of_images()))))
        self.statusbar.file_name_label.setText("{0}    {1}".format(helper.shorten(self.imgList.get_curr_img().get_file_name_or_url()),
                                                                   file_size_hr))
        self.statusbar.resolution_label.setText(f"{resolution} @ {zoom}%")
        # self.statusbar.memory_label.setText(helper.get_memory_usage())
        self.set_title(self.imgList.get_curr_img().get_file_name_only())
        if self.imgList.get_curr_img().image_state == ImageProperty.IMAGE_STATE_PROBLEM:
            self.statusbar.flash_message(red("problem"))

        p = self.img_view.geometry().topRight()
        self.loading_line.move(QPoint(p.x() - 150, p.y() + 10))

        # It's here because of preload. With this the next / prev. image appears and then the preload happens.
        # Without this preload happened and then appeared the image.
        QApplication.processEvents()

    def closeEvent(self, event):
        if self.image_info_dialog:
            self.image_info_dialog.close()
        #
        if self.important_files_and_folders_dialog:
            self.important_files_and_folders_dialog.close()
        #
        try:
            # maybe it doesn't exist at all (the window was never opened), thus we'd refer to
            # a non-existing attribute -> exception
            self.url_folding_window.close()
        except:
            pass
        #
        try:
            self.simple_scrape.close()
        except:
            pass
        #
        try:
            self.custom_url_list.close()
        except:
            pass
        #
        self.settings.write()
        #
        if self.commit.has_something_to_commit():
            msg = """You have some un-committed changes.
If you quit, you'll lose your changes.

Do you really want to quit?

Tip: hit No and commit your changes.
""".strip()
            reply = QMessageBox.question(self,
                                         'Quit Message',
                                         msg,
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
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


def main(argv):
    check_api_keys()
    #
    App = QApplication(argv)
    window = MainWindow(argv)
    window.show()
    sys.exit(App.exec())

##############################################################################

if __name__ == "__main__":
    # log.debug(sys.argv[0])
    # log.debug(sys.executable)
    main(sys.argv)
