from typing import List, Dict, Any

from jive import helper
from jive.imageproperty import ImageProperty


def _set_file_sizes(list_of_images: List[ImageProperty]) -> None:
    """
    Ask the file size of each image and register it.
    """
    for img in list_of_images:
        img.set_file_size()


def debug(d: Dict[Any, List[ImageProperty]]) -> None:
    for key, images in d.items():
        if len(images) > 1:
            print(", ".join(img.get_file_name_only() for img in images))


def _get_potential_duplicates(d: Dict[int, List[ImageProperty]]) -> List[ImageProperty]:
    result = []
    for size, images in d.items():
        if len(images) > 1:
            result.extend(images)
    #
    return result


def mark_duplicates(list_of_images: List[ImageProperty]) -> int:
    """
    Find duplicates. Keep just one and mark the others to be deleted.

    Return value: number of images that were marked to be deleted.
    """

    _set_file_sizes(list_of_images)

    # first dict.
    # key: size; value: list of img objects
    d: Dict[int, List[ImageProperty]] = {}
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
    d2: Dict[str, List[ImageProperty]] = {}
    for img in potential_duplicates:
        key = helper.file_to_md5(img.name)
        if key not in d2:
            d2[key] = []
        d2[key].append(img)

    # debug(d2)

    # Well, maybe the user has selected some images for deletion.
    # I choose this way: when there are some duplicates, I keep the first one
    # and mark the others to be deleted.

    cnt = 0

    for key, images in d2.items():
        if len(images) > 1:
            images[0].to_delete = False
            for img in images[1:]:
                img.to_delete = True
                cnt += 1

    return cnt