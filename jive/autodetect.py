from enum import Enum, auto
import re
from jive.extractors.sequence import is_valid_sequence_url
from jive import config as cfg
from pathlib import Path


class AutoDetectEnum(Enum):

    local_image = 1                                 # /home/jabba/samples/fnv.jpg
    local_folder = auto()                           # /home/jabba/samples
    #
    image_url = auto()                              # https://i.imgur.com/UamGXGe.jpg
    subreddit_url = auto()                          # https://www.reddit.com/r/wallpapers/
    subreddit_name = auto()                         # wallpapers
    subreddit_r_name = auto()                       # /r/wallpapers
    tumblr_post = auto()                            # https://different-landscapes.tumblr.com/post/174158537319
    # imgur albums and galleries are treated the same way
    imgur_album = auto()                            # https://imgur.com/a/9p0gCyv
    imgur_gallery = auto()                          # https://imgur.com/gallery/9p0gCyv
    imgur_html_page_with_embedded_image = auto()    # https://imgur.com/k489QN8 , where https://imgur.com/k489QN8.jpg is a valid image
    sequence_url = auto()                           # http://www.website.com/[001-030].jpg


def detect(text):
    """
    Detect what text is.

    The return value is a tuple, whose first element is an AutoDetectEnum.
    The tuple can have more elements that contain some extracted data.

    If text couldn't be detected, it returns None.
    """
    text = text.strip()

    if text.startswith(("http://", "https://")):
        # http://www.website.com/[001-030].jpg
        if is_valid_sequence_url(text, verbose=False):
            return (AutoDetectEnum.sequence_url, )    # 1-long tuple
        if Path(text).suffix.lower() in cfg.SUPPORTED_FORMATS:
            return (AutoDetectEnum.image_url, )    # 1-long tuple
        # https://www.reddit.com/r/EarthPorn/
        # https://reddit.com/r/EarthPorn/
        # https://old.reddit.com/r/EarthPorn/
        m = re.search(r'https?://(?:www\.|old\.)?reddit\.com/r/([^/]*)', text)
        if m:
            return (AutoDetectEnum.subreddit_url, m.group(1))
    else:
        # earthporn
        if '/' not in text:
            return (AutoDetectEnum.subreddit_name, text)
        # /r/earthporn
        # r/earthporn is invalid
        m = re.search(r'/r/([^/]*)', text)
        if m:
            return (AutoDetectEnum.subreddit_r_name, m.group(1))

    return None