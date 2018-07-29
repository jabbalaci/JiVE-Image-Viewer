#!/usr/bin/env python3

import re
import requests
from pathlib import Path
from typing import Tuple, Optional, List

from jive import config as cfg

log = cfg.log


def extract_parts_from(url: str) -> Optional[Tuple[str, str]]:
    m = re.search(r'https?://([^.]*)\.tumblr\.com/(?:post|image)/([^/]*)', url)
    if m:
        blog_name = m.group(1)
        post_id = m.group(2)
        return (blog_name, post_id)
    # else
    m = re.search(r'https?://www.tumblr.com/dashboard/blog/([^/]*)/([^/]*)', url)
    if m:
        blog_name = m.group(1)
        post_id = m.group(2)
        return (blog_name, post_id)
    # else
    return None


def is_post(url: str) -> bool:
    return extract_parts_from(url) is not None


def extract_images_from_a_specific_post(url: str) -> List[str]:
    if cfg.TUMBLR_API_KEY is None:
        log.warning(f"no tumblr API key found, cannot process {url}")
        return []
    #
    parts = extract_parts_from(url)
    # print(parts)

    result = []
    if parts:
        blog_name, post_id = parts
        # print(parsed)
        api_call = f"https://api.tumblr.com/v2/blog/{blog_name}.tumblr.com/posts/photo?id={post_id}&api_key={cfg.TUMBLR_API_KEY}"
        # print("#", api_call)
        # print()
        try:
            d = requests.get(api_call, timeout=cfg.REQUESTS_TIMEOUT).json()
        except:
            log.error(f"problem with the tumblr post {url}")
            return []
        # else
        if "errors" not in d:
            # pprint(d)
            posts = d["response"]["posts"]
            for post in posts:
                photos = post["photos"]
                for photo in photos:
                    img_url = photo["original_size"]["url"]
                    if Path(img_url).suffix.lower() in cfg.SUPPORTED_FORMATS:
                        result.append(img_url)
                #
            #
        else:
            log.warning("Unauthorized tumblr access. Is your API key valid?")
    #
    return result
