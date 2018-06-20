#!/usr/bin/env python3

"""
A simple tool with which you can verify your API keys.
"""

import re

import requests
from imgurpython import ImgurClient

# found on GitHub:
TUMBLR_API_KEY = "3Uj5hvL773MVNlhFJC5gyVftNh4Qxci3hqoPkU3nAzp9bFJ8UB"

# found on GitHub:
IMGUR_CLIENT_ID = "3cb06ab5dcf3960"
IMGUR_CLIENT_SECRET = "2215dfcb9e9ab47ddcf088c2703b0cf11ab67b08"

# IMGUR_CLIENT_ID = "199a43028219fa4"
# IMGUR_CLIENT_SECRET = "80a58bf2e3f1a6045ac11167c463ed8692bccc8d"

imgur_album_url = "https://imgur.com/gallery/9p0gCyv"    # pirates
tumblr_post_url = "https://different-landscapes.tumblr.com/post/174158537319"    # tree


def check_imgur(url):
    def get_album_id(url):
        m = re.search(r'/(?:a|gallery)/([^/?#]+)', url)
        return m.group(1) if m else None

    client = ImgurClient(IMGUR_CLIENT_ID, IMGUR_CLIENT_SECRET)
    album_id = get_album_id(url)
    images = client.get_album_images(album_id)

    return [img.link for img in images]


def check_tumblr(url):
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

    urls = []
    res = extract_parts_from(url)
    blog_name, post_id = res
    api_call = f"https://api.tumblr.com/v2/blog/{blog_name}.tumblr.com/posts/photo?id={post_id}&api_key={TUMBLR_API_KEY}"
    d = requests.get(api_call, timeout=3).json()
    if "errors" not in d:
        # pprint(d)
        posts = d["response"]["posts"]
        for post in posts:
            photos = post["photos"]
            for photo in photos:
                urls.append(photo["original_size"]["url"])
    #
    return urls


def main():
    print("Imgur result:")
    print(check_imgur(imgur_album_url))
    print("-" * 20)
    print("Tumblr result:")
    print(check_tumblr(tumblr_post_url))

##############################################################################

if __name__ == "__main__":
    main()
