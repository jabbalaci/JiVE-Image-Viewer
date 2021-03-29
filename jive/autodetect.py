import re
import requests
from enum import Enum, auto
from pathlib import Path
from typing import Union, Tuple, Optional

from jive import config as cfg
from jive.extractors import tumblr, tumblr_blog, imagefap, imgur, sequence, fuskator


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
    # we call both of them "album"
    imgur_album = auto()                            # https://imgur.com/a/9p0gCyv , https://imgur.com/gallery/9p0gCyv
    imgur_html_page_with_embedded_image = auto()    # https://imgur.com/k489QN8 , where https://imgur.com/k489QN8.jpg is a valid image
    sequence_url = auto()                           # http://www.website.com/[001-030].jpg
    imagefap_photo = auto()                         # https://www.imagefap.com/photo/1186623894/ (NSFW)
    fuskator_gallery = auto()                       # https://fuskator.com/full/aeNldhT~ia~/index.html (NSFW), or
                                                    # https://fuskator.com/thumbs/aeNldhT~ia~/index.html (NSFW)
    tumblr_blog = auto()                            # tumblr://something or https://something.tumblr.com ,
                                                    # where <something> is the name of the blog


def detect(text: str) -> Union[Tuple[AutoDetectEnum, Union[str, None]], None]:
    """
    Detect what text is.

    The return value is a 2-sized tuple, whose first element is an AutoDetectEnum.
    The second element can contain some extra data. If there's no extra data, the second element is None.

    If text couldn't be detected, it returns None.
    """
    text = text.strip()

    if text.startswith(("http://", "https://")):
        # http://www.website.com/[001-030].jpg
        if sequence.is_valid_sequence_url(text):
            return (AutoDetectEnum.sequence_url, None)
        if Path(text).suffix.lower() in cfg.SUPPORTED_FORMATS:
            return (AutoDetectEnum.image_url, None)
        # https://www.reddit.com/r/EarthPorn/
        # https://reddit.com/r/EarthPorn/
        # https://old.reddit.com/r/EarthPorn/
        m = re.search(r'https?://(?:www\.|old\.)?reddit\.com/r/([^/]*)', text)
        if m:
            return (AutoDetectEnum.subreddit_url, m.group(1))
        # https://different-landscapes.tumblr.com/post/174158537319
        if tumblr.is_post(text):
            return (AutoDetectEnum.tumblr_post, None)
        if 'imgur.com' in text:
            if imgur.is_album(text):
                return (AutoDetectEnum.imgur_album, None)
            # it's on imgur.com but it's not an album / gallery
            # it may be a single image embedded in an HTML page
            img_url = text + ".jpg"  # it works sometimes
            r = requests.head(img_url, headers=cfg.headers, timeout=cfg.REQUESTS_TIMEOUT)
            if r.ok:
                return (AutoDetectEnum.imgur_html_page_with_embedded_image, img_url)
        # endif imgur
        if imagefap.is_imagefap_photo(text):
            return (AutoDetectEnum.imagefap_photo, None)
        if fuskator.is_gallery(text):
            return (AutoDetectEnum.fuskator_gallery, None)
        if tumblr_blog.is_blog(text):
            blog_name = tumblr_blog.extract_blog_name(text)
            return (AutoDetectEnum.tumblr_blog, blog_name)
    elif text.startswith("tumblr://"):
        blog_name = tumblr_blog.extract_blog_name(text)
        return (AutoDetectEnum.tumblr_blog, blog_name)
    else:
        # earthporn
        if '/' not in text:
            return (AutoDetectEnum.subreddit_name, text)
        # /r/earthporn
        # r/earthporn is invalid
        m = re.search(r'/r/([^/]*)', text)
        if m:
            return (AutoDetectEnum.subreddit_r_name, m.group(1))
    #
    return None