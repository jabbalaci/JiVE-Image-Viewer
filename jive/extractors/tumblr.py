#!/usr/bin/env python3

import re

import requests

from jive import config as cfg
from jive import mylogging as log


def extract_parts_from(url):
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


def is_post(url):
    return extract_parts_from(url) is not None


def extract_images_from_a_specific_post(url):
    if cfg.TUMBLR_API_KEY is None:
        log.warning(f"no tumblr API key found, cannot process {url}")
        return []
    #
    res = extract_parts_from(url)
    # print(res)

    urls = []
    if res:
        blog_name, post_id = res
        # print(parsed)
        api_call = f"https://api.tumblr.com/v2/blog/{blog_name}.tumblr.com/posts/photo?id={post_id}&api_key={cfg.TUMBLR_API_KEY}"
        # print("#", api_call)
        # print()
        try:
            d = requests.get(api_call).json()
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
                    urls.append(photo["original_size"]["url"])
                #
            #
        else:
            log.warning("Unauthorized tumblr access. Is your API key valid?")
    #
    return urls
