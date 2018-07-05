import hashlib
import os
import psutil
from jive.vendor.ClusterShell.NodeSet import NodeSet
from pathlib import Path
from urllib.parse import urlparse

from jive import config as cfg

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


def string_to_md5(content):
    """
    Calculate the md5 hash of a string.
    """
    content = content.encode("utf8")
    return hashlib.md5(content).hexdigest()


def file_to_md5(filename, block_size=8192):
    """
    Calculate the md5 hash of a file. Memory-friendly solution,
    it reads the file piece by piece.

    https://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
    """
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
    #
    return md5.hexdigest()


def get_referer(url):
    """
    If an image is forbidden (status code 403), we can try using a referer.
    It works sometimes.
    """
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def remove_duplicates(lst):
    """
    Remove duplicates from a list AND keep the order of the elements.
    """
    res = []
    bag = set()
    for e in lst:
        if e not in bag:
            res.append(e)
            bag.add(e)
        #
    #
    return res


def lev_dist(s,t):
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


def clean(lines):
    """
    Remove empty lines and commented lines.
    """
    res = [line for line in lines if line.strip() and not line.strip().startswith('#')]
    return res


def filter_image_urls(lst):
    """
    Input: list of URLs.
    Output: elements in the list that are image URLs.
    """
    return [url for url in lst if Path(url).suffix.lower() in cfg.SUPPORTED_FORMATS]


def get_image_urls_only(lst):
    lst = clean(lst)
    lst = filter_image_urls(lst)
    #
    return lst


def fold_urls(lst):
    """
    The opposite of extracting (unfolding) a sequence URL. Now the input is a list of URLs
    that we want to compress (fold) to a sequence URL.

    If we forget about URLs, it's some string manipulation. Example:
    Input: ["node1", "node2", "node3"]
    Output: "node[1-3]"

    Tip from here: https://old.reddit.com/r/Python/comments/8w2737/pack_and_unpack_a_sequence_url/
    """
    res = NodeSet.fromlist(lst)    # it's a ClusterShell.NodeSet.NodeSet object
    return str(res)


def unfold_sequence_url(text):
    """
    The opposite of folding. From a sequence URL restore all the URLs (unpack, unfold).

    Input: "node[1-3]"
    Output: ["node1", "node2", "node3"]
    """
    # Create a new nodeset from string
    nodeset = NodeSet(text)
    res = [str(node) for node in nodeset]
    return res
