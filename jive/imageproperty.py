import os
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from pathlib import Path
from typing import Tuple, Optional, Union

from jive import config as cfg
from jive import fileops
from jive import helper
from jive.cache import Cache
from jive.exceptions import ImageError, FileNotSaved
from jive.helper import lightblue, red, yellow
from jive.imagewithextra import ImageWithExtraInfo

log = cfg.log


class ImageProperty:
    """
    Properties of the current (previous / next) image(s).
    """
    IMAGE_STATE_OK = 1
    IMAGE_STATE_PROBLEM = 2

    def __init__(self, img: Union[str, ImageWithExtraInfo], parent) -> None:
        if isinstance(img, ImageWithExtraInfo):
            self.name = img.fpath_or_url
            self.extra_info = img.extra_info
        else:
            self.name = img
            self.extra_info = {}
        self.local_file = self._is_local_file(self.name)
        self.parent = parent
        self.zoom_ratio = 1.0
        self.original_img: Optional[QPixmap] = None     # will be set in read()
        self.image_state: Optional[int] = None          # will be set in read()
        self.zoomed_img: Optional[QPixmap] = None       # will be set in read()
        self.file_size = -1                             # will be set in read()
        self.to_save = False
        self.to_delete = False
        self.to_wallpaper = False

    @classmethod
    def to_pixmap(cls, name: str, cache: Cache) -> Tuple[QPixmap, int, int]:
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

    def read(self, force: bool = False, preload: bool = False) -> 'ImageProperty':
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

    def free(self) -> None:
        """
        Call it when you switch to another image, thus you can free the memory
        occupied by the pixmaps (original and zoomed ones).
        """
        self.original_img = None
        self.zoomed_img = None

    def _is_local_file(self, name: str) -> bool:
        return os.path.isfile(name)

    def zoom_in(self) -> None:
        self.zoom_ratio *= 1.1
        self.calculate_zoomed_image()

    def zoom_out(self) -> None:
        self.zoom_ratio *= 0.9
        self.calculate_zoomed_image()

    def calculate_zoomed_image(self) -> QPixmap:
        if self.original_img:
            self.zoomed_img = self.original_img.scaled(self.zoom_ratio * self.original_img.width(),
                                                       self.zoom_ratio * self.original_img.height(),
                                                       Qt.KeepAspectRatio,
                                                       Qt.SmoothTransformation)
        return self.zoomed_img

    def set_zoomed_img(self, pm: QPixmap) -> None:
        self.zoomed_img = pm
        # If there's a problem with an image, we return not_found.png,
        # thus division by 0 cannot happen here.
        if pm and self.original_img:
            self.zoom_ratio = pm.width() / self.original_img.width()

    def zoom_reset(self) -> None:
        self.zoom_ratio = 1.0
        self.zoomed_img = self.original_img

    def fit_img_to_window(self) -> None:
        width, height = self.parent.available_width_and_height()
        if self.original_img:
            pm = self.original_img.scaled(width,
                                          height,
                                          Qt.KeepAspectRatio,
                                          Qt.SmoothTransformation)
            self.set_zoomed_img(pm)

    def fit_img_to_window_width(self) -> None:
        window_width = self.parent.geometry().width()
        new_width = window_width * (cfg.IMG_WIDTH_TO_WINDOW_WIDTH_IN_PERCENT / 100)
        new_height = new_width / self.get_aspect_ratio()
        if self.original_img:
            pm = self.original_img.scaled(new_width,
                                          new_height,
                                          Qt.KeepAspectRatio,
                                          Qt.SmoothTransformation)
            self.set_zoomed_img(pm)

    def get_file_name_only(self) -> str:
        return str(Path(self.name).name)

    def get_file_name_or_url(self) -> str:
        if self.local_file:
            return str(Path(self.name).name)
        else:
            return self.name

    def get_absolute_path_or_url(self) -> str:
        if self.local_file:
            return str(Path(self.name).absolute())
        else:
            return self.name

    def get_aspect_ratio(self) -> float:
        return self.original_img.width() / self.original_img.height()    # type: ignore

    def get_file_size(self, human_readable: bool = False) -> Union[int, str]:
        if not human_readable:
            return self.file_size
        else:
            return helper.file_size_fmt(self.file_size) if self.file_size > -1 else ""

    def toggle_save(self) -> None:
        self.to_save = not self.to_save

    def toggle_delete(self) -> None:
        self.to_delete = not self.to_delete

    def toggle_wallpaper(self) -> None:
        self.to_wallpaper = not self.to_wallpaper

    def set_file_size(self) -> None:
        self.file_size = os.path.getsize(self.name)

    def get_flags(self) -> str:
        sb = []
        if self.to_save:
            sb.append("save")
        if self.to_delete:
            sb.append("delete")
        if self.to_wallpaper:
            sb.append("wallpaper")
        return ", ".join(sb) if sb else "--"

    def get_short_flags(self) -> str:
        sb = []
        if self.to_save:
            sb.append(yellow("S"))
        if self.to_delete:
            sb.append(red("D"))
        if self.to_wallpaper:
            sb.append(lightblue("W"))
        return "<br>".join(sb)

    def is_it_in_a_subreddit(self) -> bool:
        """
        If this image is in a subreddit, return True.
        Else, return False.
        """
        return "subreddit" in self.extra_info

    def is_it_really_the_last(self) -> bool:
        """
        Return True if this image is really the last and there is no way to load more images.
        For instance: we open a folder.

        At the moment there is only one possibility to load more images: when we open a subreddit.
        So, if we are in a subreddit, False is returned.
        """
        if self.is_it_in_a_subreddit():
            return False

        return True

    def save_to_filesystem(self, folder: str, method: int) -> bool:
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

    def save_as(self, dest: str) -> bool:
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
