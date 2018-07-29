"""
File operations, namely:

* save image to a local folder
* delete a local image

"""

import os
import requests
import shutil
from pathlib import Path

from jive.cache import Cache
from jive import config as cfg

log = cfg.log


def generate_new_name(old_name_with_ext: str, folder: str) -> str:
    """
    Generate a new name for the file.

    Say there is already a file called "01.jpg".
    In this case, the function returns "01-2.jpg".
    """
    old = Path(old_name_with_ext)
    old_name = old.stem
    ext = old.suffix

    cnt = 1
    while True:
        cnt += 1    # start with value 2
        p = Path(folder, f"{old_name}-{cnt}{ext}")
        if not p.exists():
            return str(p)


def save(img, folder: str, cache: Cache) -> bool:
    """
    Save the given image to the specified folder.

    Return True, if saving was successful. False, otherwise.
    """

    src = img.get_absolute_path_or_url()
    name_only = img.get_file_name_only()
    dest = str(Path(folder, name_only))

    found_in_cache = False
    if cache.enabled() and (not img.local_file) and src in cache:
        found_in_cache = True
        url = src
        # log.debug(f"image save: {url} was found in the cache")
        fname = cache.get_fname_to_url(url)
        img.file_size = os.path.getsize(fname)

    # requests object; later, if it's still None, will be set properly
    r = None
    if (not img.local_file) and (img.get_file_size() == -1):
        # Goal: if it's a URL whose file size is unknown => figure out its file size
        # Why do we need the file size? If there's a destination with the same name,
        # then we compare the file sizes to tell if they are identical or not.
        # If the image is in the cache, then in the previous step we set the file size,
        # so in that case we don't connect to the URL.
        url = src
        r = requests.get(url, headers=cfg.headers, timeout=cfg.REQUESTS_TIMEOUT)
        try:
            file_size = int(r.headers['Content-Length'])
        except:
            file_size = -1
        #
        img.file_size = file_size
        log.debug(f"file size: {img.get_file_size()}")

    # if the save target exists with this name, then there are 2 cases
    if os.path.isfile(dest):
        if os.path.getsize(dest) == img.get_file_size():
            # 1) the file size is the same => very likely they are identical => no need to overwrite it
            return True
        else:
            # 2) the file size is different => different image
            # as it has the same name, generate a new name for the target
            new_name = generate_new_name(name_only, folder)
            dest = str(Path(folder, new_name))    # re-assign value to it

    if img.local_file:
        # local file
        shutil.copy(src, dest)
        if os.path.isfile(dest) and os.path.getsize(dest) == os.path.getsize(src):
            return True
    else:
        # URL
        url = src

        if found_in_cache:
            fname = cache.get_fname_to_url(url)
            shutil.copy(fname, dest)
            if os.path.isfile(dest) and os.path.getsize(dest) == os.path.getsize(fname):
                return True

        # if it's not in the cache
        # if it was set before, then don't connect again
        if r is None:
            r = requests.get(url, headers=cfg.headers, timeout=cfg.REQUESTS_TIMEOUT)
        if r.status_code == 200:
            with open(dest, 'wb') as f:
                f.write(r.content)
            if os.path.isfile(dest) and os.path.getsize(dest) > 0:
                return True
    #
    return False


def save_as(img, cache: Cache, dest: str) -> bool:
    """
    Save the given image to dest (where dest is the absolute path of the destination).

    Return True, if saving was successful. False, otherwise.
    """

    src = img.get_absolute_path_or_url()

    found_in_cache = False
    if cache.enabled() and (not img.local_file) and src in cache:
        found_in_cache = True
        url = src
        # log.debug(f"image save: {url} was found in the cache")
        fname = cache.get_fname_to_url(url)
        img.file_size = os.path.getsize(fname)

    # requests object; later, if it's still None, will be set properly
    r = None
    if (not img.local_file) and (img.get_file_size() == -1):
        # Goal: if it's a URL whose file size is unknown => figure out its file size
        # Why do we need the file size? If there's a destination with the same name,
        # then we compare the file sizes to tell if they are identical or not.
        # If the image is in the cache, then in the previous step we set the file size,
        # so in that case we don't connect to the URL.
        url = src
        r = requests.get(url, headers=cfg.headers, timeout=cfg.REQUESTS_TIMEOUT)
        try:
            file_size = int(r.headers['Content-Length'])
        except:
            file_size = -1
        #
        img.file_size = file_size
        log.debug(f"file size: {img.get_file_size()}")

    if img.local_file:
        # local file
        shutil.copy(src, dest)
        if os.path.isfile(dest) and os.path.getsize(dest) == os.path.getsize(src):
            return True
    else:
        # URL
        url = src

        if found_in_cache:
            fname = cache.get_fname_to_url(url)
            shutil.copy(fname, dest)
            if os.path.isfile(dest) and os.path.getsize(dest) == os.path.getsize(fname):
                return True

        # if it's not in the cache
        # if it was set before, then don't connect again
        if r is None:
            r = requests.get(url, headers=cfg.headers, timeout=cfg.REQUESTS_TIMEOUT)
        if r.status_code == 200:
            with open(dest, 'wb') as f:
                f.write(r.content)
            if os.path.isfile(dest) and os.path.getsize(dest) > 0:
                return True
    #
    return False