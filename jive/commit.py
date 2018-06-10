"""
Take care of flagged images.

s - save the image
d - delete the image
w - save image to a wallpaper folder
"""

class Commit:
    def __init__(self, parent):
        self.parent = parent

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

    def has_something_not_yet_committed(self):
        val1 = self.to_save()
        val2 = self.to_delete()
        val3 = self.to_wallpaper()

        return any([val1, val2, val3])