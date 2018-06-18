"""
File operations, namely:

* save image to a local folder
* delete a local image

"""

import os
import requests
import shutil
from pathlib import Path

from jive import config as cfg
from jive import mylogging as log


def generate_new_name(old_name_with_ext, folder):
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


def save(img, folder):
    """
    Save the given image to the specified folder.

    Return True, if saving was successful. False, otherwise.
    """

    src = img.get_absolute_path_or_url()
    name_only = img.get_file_name_only()
    dest = str(Path(folder, name_only))

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
        r = requests.get(url, headers=cfg.headers, timeout=cfg.REQUESTS_TIMEOUT)
        if r.status_code == 200:
            with open(dest, 'wb') as f:
                f.write(r.content)
            if os.path.isfile(dest) and os.path.getsize(dest) > 0:
                return True
    #
    return False