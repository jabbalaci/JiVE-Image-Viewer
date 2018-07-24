from typing import Dict

from jive import helper


def _set_file_sizes(list_of_images) -> None:
    """
    Ask the file size of each image and register it.
    """
    for img in list_of_images:
        img.set_file_size()


def debug(d: Dict) -> None:
    for key, images in d.items():
        if len(images) > 1:
            print(", ".join(img.get_file_name_only() for img in images))


def _get_potential_duplicates(d):
    result = []
    for size, images in d.items():
        if len(images) > 1:
            result.extend(images)
    #
    return result


def mark_duplicates(list_of_images) -> int:
    """
    Find duplicates. Keep just one and mark the others to be deleted.

    Return value: number of images that were marked to be deleted.
    """

    _set_file_sizes(list_of_images)

    # first dict.
    # key: size; value: list of img objects
    d: Dict = {}
    for img in list_of_images:
        size = img.file_size
        if size not in d:
            d[size] = []
        d[size].append(img)

    # debug(d)

    potential_duplicates = _get_potential_duplicates(d)
    # print(", ".join(img.get_file_name_only() for img in potential_duplicates))

    # second dict.
    # key: md5 hash of the file's content; value: list of img objects
    d = {}
    for img in potential_duplicates:
        key = helper.file_to_md5(img.name)
        if key not in d:
            d[key] = []
        d[key].append(img)

    # debug(d)

    # Well, maybe the user has selected some images for deletion.
    # I choose this way: when there are some duplicates, I keep the first one
    # and mark the others to be deleted.

    cnt = 0

    for key, images in d.items():
        if len(images) > 1:
            images[0].to_delete = False
            for img in images[1:]:
                img.to_delete = True
                cnt += 1

    return cnt