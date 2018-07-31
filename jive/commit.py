"""
Take care of flagged images.

s - save the image
d - delete the image
w - save image to a wallpaper folder
"""

from time import sleep

from PyQt5.QtWidgets import QApplication
from pathlib import Path
from typing import List

from jive import config as cfg
from jive.imageproperty import ImageProperty

log = cfg.log


class Commit:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.statusbar = self.parent.statusbar
        self.message_label = self.statusbar.message_label
        self.progressbar = self.statusbar.progressbar

    def has_something_to_commit(self) -> bool:
        return bool(self.parent.imgList.has_something_to_commit())

    def to_save(self) -> int:
        """
        Number of images flagged to be saved.
        """
        return int(self.parent.imgList.to_save())

    def to_delete(self) -> int:
        """
        Number of images flagged to be deleted.
        """
        return int(self.parent.imgList.to_delete())

    def to_wallpaper(self) -> int:
        """
        Number of images flagged to be saved as wallpapers.
        """
        return int(self.parent.imgList.to_wallpaper())

    def _save_files(self, folder: str, lst: List[ImageProperty], msg: str, method: int) -> int:
        """
        Save images in `lst` to the specified folder.

        Return the number of images that were saved successfully.
        """
        total = len(lst)
        cnt = 0

        for idx, img in enumerate(lst, start=1):
            percent = round(idx * 100 / total)
            cnt += img.save_to_filesystem(folder, method)

            log.info(f"{msg} {percent}%")
            self.message_label.setText(msg)
            self.progressbar.show()
            self.progressbar.setValue(percent)
            QApplication.processEvents()
        #
        sleep(0.2)    # make the progressbar visible
        self.message_label.setText("")
        self.progressbar.hide()

        return cnt

    def save_wallpapers(self) -> int:
        """
        Save all the images that were marked as wallpapers.

        Return the number of images that were saved successfully.
        """
        folder = cfg.PLATFORM_SETTINGS['wallpapers_dir']
        lst = [img for img in self.parent.imgList.get_list_of_images() if img.to_wallpaper]

        return self._save_files(folder, lst, "saving wallpapers", cfg.WALLPAPER_SAVE)

    def save_others(self) -> int:
        """
        Save all the images that were marked to be saved.

        Return the number of images that were saved successfully.
        """
        folder = cfg.PLATFORM_SETTINGS['saves_dir']
        lst = [img for img in self.parent.imgList.get_list_of_images() if img.to_save]

        return self._save_files(folder, lst, "saving", cfg.NORMAL_SAVE)

    def delete_files(self) -> int:
        if self.to_delete() == 0:
            return 0
        # else, there's something to delete
        pos_img = None
        if not self.parent.imgList.get_curr_img().to_delete:
            # we don't want to delete the current image
            pos_img = self.parent.imgList.get_curr_img()
        else:
            # we want to delete the current image
            images_to_keep_right = [img for img in self.parent.imgList.get_list_of_images()[self.parent.imgList.get_curr_img_idx() + 1:] if
                                    not img.to_delete]
            if len(images_to_keep_right) > 0:
                pos_img = images_to_keep_right[0]
            else:
                images_to_keep_left = [img for img in self.parent.imgList.get_list_of_images()[:self.parent.imgList.get_curr_img_idx()] if
                                       not img.to_delete]
                if len(images_to_keep_left) > 0:
                    pos_img = images_to_keep_left[-1]
        #
        to_delete = [img for img in self.parent.imgList.get_list_of_images() if img.to_delete]
        result = self.delete_physically(to_delete)

        to_keep = [img for img in self.parent.imgList.get_list_of_images() if not img.to_delete]
        self.parent.imgList.set_list_of_images(to_keep)
        if len(to_keep) > 0:
            # there are remaining images, thus pos_img points to an image that we want to keep
            idx = self.parent.imgList.get_list_of_images().index(pos_img)
            # log.debug(f"index: {idx}")
            self.parent.imgList.jump_to_image_and_dont_care_about_the_previous_image(idx)
        else:
            self.parent.reset()

        # how many images were removed successfully
        return result

    def delete_physically(self, death_list: List[ImageProperty]) -> int:
        """
        Delete the images in the list from the file system.

        Return value: number of images that were removed successfully.
        """
        total = len(death_list)
        cnt = 0
        msg = "deleting"

        for idx, img in enumerate(death_list, start=1):
            percent = round(idx * 100 / total)
            log.info(f"{msg} {percent}%")
            self.message_label.setText(msg)
            self.progressbar.show()
            self.progressbar.setValue(percent)
            QApplication.processEvents()

            p = Path(img.get_absolute_path_or_url())
            # log.debug(f"removing {str(p)}")
            p.unlink()
            if not p.exists():
                cnt += 1
            else:
                log.warning(f"couldn't remove {str(p)}")
        #
        sleep(0.2)  # make the progressbar visible
        self.message_label.setText("")
        self.progressbar.hide()
        #
        return cnt
