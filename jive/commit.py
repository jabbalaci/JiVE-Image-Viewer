"""
Take care of flagged images.

s - save the image
d - delete the image
w - save image to a wallpaper folder
"""

from pathlib import Path
from time import sleep

from PyQt5.QtWidgets import QApplication

from jive import config as cfg
from jive import mylogging as log


class Commit:
    def __init__(self, parent):
        self.parent = parent
        self.statusbar = self.parent.statusbar
        self.message_label = self.statusbar.message_label
        self.progressbar = self.statusbar.progressbar

    def to_save(self):
        """
        Number of images flagged to be saved.
        """
        return sum(1 for img in self.parent.list_of_images if img.to_save)

    def to_delete(self):
        """
        Number of images flagged to be deleted.
        """
        return sum(1 for img in self.parent.list_of_images if img.to_delete)

    def to_wallpaper(self):
        """
        Number of images flagged to be saved as wallpapers.
        """
        return sum(1 for img in self.parent.list_of_images if img.to_wallpaper)

    def has_something_to_commit(self):
        val1 = self.to_save()
        val2 = self.to_delete()
        val3 = self.to_wallpaper()

        return any([val1, val2, val3])

    def _save_files(self, folder, lst, msg, method):
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

    def save_wallpapers(self):
        """
        Save all the images that were marked as wallpapers.

        Return the number of images that were saved successfully.
        """
        folder = cfg.PLATFORM_SETTINGS['wallpapers_dir']
        lst = [img for img in self.parent.list_of_images if img.to_wallpaper]

        return self._save_files(folder, lst, "saving wallpapers", cfg.WALLPAPER_SAVE)

    def save_others(self):
        """
        Save all the images that were marked to be saved.

        Return the number of images that were saved successfully.
        """
        folder = cfg.PLATFORM_SETTINGS['saves_dir']
        lst = [img for img in self.parent.list_of_images if img.to_save]

        return self._save_files(folder, lst, "saving", cfg.NORMAL_SAVE)

    def delete_files(self):
        if self.to_delete() == 0:
            return 0
        # else, there's something to delete
        pos_img = None
        if not self.parent.curr_img.to_delete:
            # we don't want to delete the current image
            pos_img = self.parent.curr_img
        else:
            # we want to delete the current image
            images_to_keep_right = [img for img in self.parent.list_of_images[self.parent.curr_img_idx + 1:] if
                                    not img.to_delete]
            if len(images_to_keep_right) > 0:
                pos_img = images_to_keep_right[0]
            else:
                images_to_keep_left = [img for img in self.parent.list_of_images[:self.parent.curr_img_idx] if
                                       not img.to_delete]
                if len(images_to_keep_left) > 0:
                    pos_img = images_to_keep_left[-1]
        #
        to_delete = [img for img in self.parent.list_of_images if img.to_delete]
        result = self.delete_physically(to_delete)

        to_keep = [img for img in self.parent.list_of_images if not img.to_delete]
        self.parent.list_of_images = to_keep
        if len(to_keep) > 0:
            # there are remaining images, thus pos_img points to an image that we want to keep
            idx = self.parent.list_of_images.index(pos_img)
            # log.debug(f"index: {idx}")
            self.parent.jump_to_image_and_dont_care_about_the_previous_image(idx)
        else:
            self.parent.reset()

        # how many images were removed successfully
        return result

    def delete_physically(self, death_list):
        """
        Delete the images in the list from the file system.

        Return value: number of images that were removed successfully.
        """
        cnt = 0
        for img in death_list:
            p = Path(img.get_absolute_path_or_url())
            log.debug(f"removing {str(p)}")
            p.unlink()
            if not p.exists():
                cnt += 1
        #
        return cnt
