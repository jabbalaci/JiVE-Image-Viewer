import config as cfg
import os
from pathlib import Path

import psutil

BYTE = 1
KB = 1024 * BYTE
MB = 1024 * KB
GB = 1024 * MB
TB = 1024 * GB


def read_image_files(dir_path):
    res = []
    for f in sorted(os.listdir(dir_path)):
        if Path(f).suffix.lower() in cfg.SUPPORTED_FORMATS:
            res.append(str(Path(dir_path, f)))
        #
    #
    return res


def pretty_num(num):
    """
    Prettify a large number, e.g. 1977 -> "1,977".
    """
    return "{:,}".format(num)


def sizeof_fmt(num):
    """
    Convert memory consumption to human readable format.
    """
    for x in ['b', 'K', 'M', 'G', 'T']:
        if num < 1024:
            return "{0}{1}".format(round(num), x)
        num /= 1024


def file_size_fmt(num):
    """
    Convert file size to human readable format.
    """
    for x in ['bytes', 'kB', 'MB', 'GB', 'TB']:
        if num < 1000:
            return "{0} {1}".format(round(num, 1), x)
        num /= 1000


def get_memory_usage():
    process = psutil.Process(os.getpid())
    in_bytes = process.memory_info().rss
    return sizeof_fmt(in_bytes)


def color(col, text, bold=True):
    if bold:
        return f"<font color='{col}'><strong>{text}</strong></font>"
    # else
    return f"<font color='{col}'>{text}</font>"


def green(text, bold=True):
    """
    Hacker green :)
    """
    return color("#04ff02", text, bold)


def red(text, bold=True):
    return color("red", text, bold)


def blue(text, bold=True):
    return color("blue", text, bold)


def yellow(text, bold=True):
    return color("yellow", text, bold)


def lightblue(text, bold=True):
    return color("#ACB1E6", text, bold)


def gray(text, bold=True):
    return color("gray", text, bold)


def bold(text):
    return f"<strong>{text}</strong>"


def get_screen_size(app):
    screen = app.primaryScreen()
    size = screen.size()
    return (size.width(), size.height())


def get_screen_available_geometry(app):
    screen = app.primaryScreen()
    rect = screen.availableGeometry()
    return (rect.width(), rect.height())


def shorten(text, length=40):
    if len(text) <= length:
        return text
    # else
    half = length // 2
    return f"{text[:half]}...{text[-half:]}"
