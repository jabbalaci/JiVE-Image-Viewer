"""
Take care of flagged images.

s - save the image
d - delete the image
w - save image to a wallpaper folder
"""

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
        return 0