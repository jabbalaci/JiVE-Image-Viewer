import webbrowser
import hashlib
import os
import psutil
import requests
from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import (QApplication)
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Tuple, List, Any, Set, Optional
from urllib.parse import urlparse

from jive import config as cfg
from jive.vendor.ClusterShell.NodeSet import NodeSet

log = cfg.log

BYTE = 1
KB = 1024 * BYTE
MB = 1024 * KB
GB = 1024 * MB
TB = 1024 * GB


def read_image_files(dir_path: str) -> List[str]:
    result = []
    for f in sorted(os.listdir(dir_path)):
        if Path(f).suffix.lower() in cfg.SUPPORTED_FORMATS:
            result.append(str(Path(dir_path, f)))
        #
    #
    return result


def get_page_as_requests_object(url: str) -> Optional[requests.Response]:
    """
    Get a webpage and return it as a requests Response object.
    """
    try:
        r = requests.get(url, headers=cfg.headers, timeout=cfg.REQUESTS_TIMEOUT)
        return r
    except:
        log.warning(f"couldn't get {url}")
        return None


def get_page_as_text(url: str) -> Optional[str]:
    """
    Get a webpage and return its HTML content as a string.
    """
    r = get_page_as_requests_object(url)
    if r:
        return r.text
    #
    return None


def get_page_as_soup(url: str) -> Optional[BeautifulSoup]:
    """
    Get a webpage and return its HTML content as a BeautifulSoup object.
    """
    html = get_page_as_text(url)
    if html:
        return BeautifulSoup(html, "lxml")
    #
    return None


def pretty_num(num: int) -> str:
    """
    Prettify a large number, e.g. 1977 -> "1,977".
    """
    return "{:,}".format(num)


def sizeof_fmt(num: int) -> str:
    """
    Convert memory consumption to human readable format.
    """
    value = float(num)

    result = ""
    for x in ['b', 'K', 'M', 'G', 'T']:
        if value < 1024:
            result = "{0}{1}".format(round(value), x)
            break
        value /= 1024
    #
    return result


def file_size_fmt(num: int) -> str:
    """
    Convert file size to human readable format.
    """
    value = float(num)

    result = ""
    for x in ['bytes', 'kB', 'MB', 'GB', 'TB']:
        if value < 1000:
            result = "{0} {1}".format(round(value, 1), x)
            break
        value /= 1000
    #
    return result


def get_memory_usage() -> str:
    process = psutil.Process(os.getpid())
    in_bytes: int = process.memory_info().rss
    return sizeof_fmt(in_bytes)


def color(col: str, text: str, bold: bool = True) -> str:
    if bold:
        return f"<font color='{col}'><strong>{text}</strong></font>"
    # else
    return f"<font color='{col}'>{text}</font>"


def green(text: str, bold: bool = True) -> str:
    """
    Hacker green :)
    """
    return color("#04ff02", text, bold)


def red(text: str, bold: bool = True) -> str:
    return color("red", text, bold)


def blue(text: str, bold: bool = True) -> str:
    return color("blue", text, bold)


def yellow(text: str, bold: bool = True) -> str:
    return color("yellow", text, bold)


def lightblue(text: str, bold: bool = True) -> str:
    return color("#ACB1E6", text, bold)


def gray(text: str, bold: bool = True) -> str:
    return color("gray", text, bold)


def bold(text: str) -> str:
    return f"<strong>{text}</strong>"


def get_screen_size(app) -> Tuple[int, int]:
    screen = app.primaryScreen()
    size = screen.size()
    return (size.width(), size.height())


def get_screen_available_geometry(app) -> Tuple[int, int]:
    screen = app.primaryScreen()
    rect = screen.availableGeometry()
    return (rect.width(), rect.height())


def shorten(text: str, length: int = 40) -> str:
    if len(text) <= length:
        return text
    # else
    half = length // 2
    return f"{text[:half]}...{text[-half:]}"


def string_to_md5(text: str) -> str:
    """
    Calculate the md5 hash of a string.
    """
    raw: bytes = text.encode("utf8")
    return hashlib.md5(raw).hexdigest()


def file_to_md5(fname: str, block_size: int = 8192) -> str:
    """
    Calculate the md5 hash of a file. Memory-friendly solution,
    it reads the file piece by piece.

    https://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
    """
    md5 = hashlib.md5()
    with open(fname, 'rb') as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
    #
    return md5.hexdigest()


def get_referer(url: str) -> str:
    """
    If an image is forbidden (status code 403), we can try using a referer.
    It works sometimes.
    """
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def remove_duplicates(lst: List[Any]) -> List[Any]:
    """
    Remove duplicates from a list AND keep the order of the elements.
    """
    result: List[Any] = []
    bag: Set[Any] = set()
    for e in lst:
        if e not in bag:
            result.append(e)
            bag.add(e)
        #
    #
    return result


def lev_dist(s: str, t: str) -> int:
    """
    The Levenshtein distance (or edit distance) between two strings
    is the minimal number of "edit operations" required to change
    one string into the other. The two strings can have different
    lengths. There are three kinds of "edit operations": deletion,
    insertion, or alteration of a character in either string.

    Example: the Levenshtein distance of "ag-tcc" and "cgctca" is 3.
    source: http://en.wikibooks.org/wiki/Algorithm_implementation/Strings/Levenshtein_distance#Python
    """
    s = ' ' + s
    t = ' ' + t
    d = {}
    S = len(s)
    T = len(t)
    for i in range(S):
        d[i, 0] = i
    for j in range (T):
        d[0, j] = j
    for j in range(1,T):
        for i in range(1,S):
            if s[i] == t[j]:
                d[i, j] = d[i-1, j-1]
            else:
                d[i, j] = min(d[i-1, j] + 1, d[i, j-1] + 1, d[i-1, j-1] + 1)
    return d[S-1, T-1]


def clean(lines: List[str]) -> List[str]:
    """
    Remove empty lines and commented lines.
    """
    return [line for line in lines if line.strip() and not line.strip().startswith('#')]


def filter_image_urls(lst: List[str]) -> List[str]:
    """
    Input: list of URLs.
    Output: elements in the list that are image URLs.
    """
    return [url for url in lst if Path(url).suffix.lower() in cfg.SUPPORTED_FORMATS]


def get_image_urls_only(lst: List[str]) -> List[str]:
    lst = clean(lst)
    lst = filter_image_urls(lst)
    #
    return lst


def fold_urls(lst: List[str]) -> str:
    """
    The opposite of extracting (unfolding) a sequence URL. Now the input is a list of URLs
    that we want to compress (fold) to a sequence URL.

    If we forget about URLs, it's some string manipulation. Example:
    Input: ["node1", "node2", "node3"]
    Output: "node[1-3]"

    Tip from here: https://old.reddit.com/r/Python/comments/8w2737/pack_and_unpack_a_sequence_url/
    """
    result = NodeSet.fromlist(lst)    # it's a ClusterShell.NodeSet.NodeSet object
    return str(result)


def unfold_sequence_url(text: str) -> List[str]:
    """
    The opposite of folding. From a sequence URL restore all the URLs (unpack, unfold).

    Input: "node[1-3]"
    Output: ["node1", "node2", "node3"]
    """
    # Create a new nodeset from string
    nodeset = NodeSet(text)
    result = [str(node) for node in nodeset]
    return result


def copy_text_to_clipboard(text: str) -> None:
    cb: QClipboard = QApplication.clipboard()
    cb.setText(text)


def get_text_from_clipboard() -> str:
    cb: QClipboard = QApplication.clipboard()
    return str(cb.text())

def open_new_browser_tab(url: str) -> None:
    webbrowser.open_new_tab(url)