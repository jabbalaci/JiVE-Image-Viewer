import random
from PyQt5.QtWidgets import (QMessageBox)
from typing import Optional, List

from jive import config as cfg
from jive.extractors import subreddit
from jive.helper import red, blue
from jive.imageproperty import ImageProperty


class ImageList:
    def __init__(self, parent) -> None:
        self.mainWindow = parent
        self.reset()

        self._prev_random_img_idx = -1

    def reset(self) -> None:
        self._list_of_images: List[ImageProperty] = []
        self._curr_img_idx = -1
        self._curr_img = None

    def get_curr_img(self) -> Optional[ImageProperty]:
        return self._curr_img

    def set_curr_img(self, img) -> None:
        self._curr_img = img

    def get_curr_img_idx(self) -> int:
        return self._curr_img_idx

    def set_curr_img_idx(self, idx: int) -> None:
        self._curr_img_idx = idx

    def get_list_of_images(self) -> List[ImageProperty]:
        return self._list_of_images

    def set_list_of_images(self, lst: List[ImageProperty]) -> None:
        self._list_of_images = lst

    def _find_image_index_by_name(self, name: str) -> int:
        for i in range(len(self._list_of_images)):
            if self._list_of_images[i].name == name:
                return i
            #
        #
        return -1    # not found

    def shuffle_images(self) -> None:
        # if there are no images or if there is only one, shuffle makes no sense
        length = len(self._list_of_images)
        if (length == 0) or (length == 1):
            self.mainWindow.statusbar.flash_message(blue("done"))
            return
        # else
        name = self._curr_img.name    # type: ignore
        old_name = self._curr_img.name    # type: ignore
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

    def jump_to_next_image(self) -> None:
        if len(self._list_of_images) == 0:
            self.mainWindow.statusbar.flash_message(red("no more"), wait=cfg.MESSAGE_FLASH_TIME_1)
            self.mainWindow.play_error_sound()
            return
        # else
        if self._curr_img_idx == len(self._list_of_images) - 1:
            self.mainWindow.statusbar.flash_message(red("no more"), wait=cfg.MESSAGE_FLASH_TIME_1)
            if self._curr_img.is_it_really_the_last():    # type: ignore
                self.mainWindow.play_error_sound()
            img = self._curr_img
            subreddit_name = img.extra_info.get("subreddit")    # type: ignore
            after_id = img.extra_info.get("after_id")    # type: ignore
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
                    QMessageBox.information(self.mainWindow,
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

    def jump_to_first_image(self) -> None:
        self.jump_to_image(0)

    def jump_to_last_image(self) -> None:
        new_idx = len(self._list_of_images) - 1
        self.jump_to_image(new_idx)

    def jump_to_prev_image(self) -> None:
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

    def jump_five_percent_forward(self) -> None:
        offset = round(5 * len(self._list_of_images) / 100)
        self.jump_to_image(self._curr_img_idx + offset)

    def jump_five_percent_backward(self) -> None:
        offset = round(5 * len(self._list_of_images) / 100)
        self.jump_to_image(self._curr_img_idx - offset)

    def jump_to_image(self, new_idx: int) -> None:
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
        self._curr_img = self._list_of_images[self._curr_img_idx].read()    # type: ignore
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

    def jump_to_image_and_dont_care_about_the_previous_image(self, idx: int) -> None:
        self._curr_img_idx = idx
        #
        if self._curr_img_idx >= len(self._list_of_images):
            self._curr_img_idx = len(self._list_of_images) - 1
        if self._curr_img_idx < 0:
            self._curr_img_idx = 0
        #
        self._curr_img = self._list_of_images[self._curr_img_idx].read()    # type: ignore
        self.mainWindow.scroll_to_top()
        self.mainWindow.redraw()
        #
        if self.mainWindow.preload:
            self.preload_next_image()
            self.preload_prev_image()

        # let's always call it (with and without preload), just to be sure to free memory
        self.free_others()

    def preload_next_image(self) -> None:
        try:
            next_img = self._list_of_images[self._curr_img_idx + 1]
            next_img.read(preload=True)
        except IndexError:
            pass    # we are at the last image, there's no next one

    def preload_prev_image(self) -> None:
        try:
            minus_1 = self._curr_img_idx - 1
            if minus_1 < 0:
                raise IndexError
            prev_img = self._list_of_images[minus_1]
            prev_img.read(preload=True)
        except IndexError:
            pass    # we are at the beginning, there's no previous one

    def free_others(self) -> None:
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

    def jump_to_random_image(self) -> None:
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

    def jump_to_prev_random_image(self) -> None:
        if self._prev_random_img_idx == -1:
            return
        # else
        jump_to = self._prev_random_img_idx
        self._prev_random_img_idx = self._curr_img_idx  # save where we were
        self.jump_to_image(jump_to)

    def to_save(self) -> int:
        """
        Number of images flagged to be saved.
        """
        return sum(1 for img in self._list_of_images if img.to_save)

    def to_delete(self) -> int:
        """
        Number of images flagged to be deleted.
        """
        return sum(1 for img in self._list_of_images if img.to_delete)

    def to_wallpaper(self) -> int:
        """
        Number of images flagged to be saved as wallpapers.
        """
        return sum(1 for img in self._list_of_images if img.to_wallpaper)

    def has_something_to_commit(self) -> bool:
        val1 = self.to_save()
        val2 = self.to_delete()
        val3 = self.to_wallpaper()

        return any([val1, val2, val3])

    def mark_all_images_to_save(self) -> None:
        for img in self._list_of_images:
            img.to_save = True

    def get_image_list(self) -> List[str]:
        """
        Return the path / URL of the images that are in the current list.
        """
        result = [img.get_absolute_path_or_url() for img in self._list_of_images]
        return result