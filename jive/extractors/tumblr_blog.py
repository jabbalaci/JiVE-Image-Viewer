import re
from typing import Any, Dict, List, Optional

import pytumblr
from jive import config as cfg
from jive.debug import save_json
from jive.imagewithextra import ImageWithExtraInfo
from PyQt5.QtWidgets import QApplication

log = cfg.log

# SAVE_JSON = True    # for debug
SAVE_JSON = False


def extract_blog_name(text: str) -> Optional[str]:
    if text.startswith("tumblr://"):
        blog_name = text.split("://")[1]
        return blog_name
    if text.startswith("http"):
        m = re.search(r'^https?://([^.]*)\.tumblr\.com/?$', text)
        if m:
            blog_name = m.group(1)
            return blog_name
    #
    return None


def is_blog(url: str) -> bool:
    return extract_blog_name(url) is not None


def extract_photo_urls(li: List[Dict[str, Any]]) -> List[str]:
    result = []

    for d in li:
        photo_set: List[Dict] = d["photos"]
        for photo in photo_set:
            url = photo["original_size"]["url"]
            if not url.lower().endswith(".gif"):
                result.append(url)

    return result


def get_photo_urls(blog_name: str, offset=0, statusbar=None, mainWindow=None) -> List[ImageWithExtraInfo]:
    try:
        if mainWindow:
            mainWindow.loading_line.show()
        log.info(f"tumblr blog: '{blog_name}'")
        blog_obj = pytumblr.TumblrRestClient(
            cfg.TUMBLR_CONSUMER_KEY,
            cfg.TUMBLR_CONSUMER_SECRET,
            cfg.TUMBLR_TOKEN_KEY,
            cfg.TUMBLR_TOKEN_SECRET,
        )
        #
        d = blog_obj.posts(blog_name)
        if SAVE_JSON:
            save_json.save(d)
        total_posts = d['blog']['total_posts']
        log.info(f"total posts on tumblr blog '{blog_name}': {total_posts}")
        urls = []
        while offset < total_posts:
            li = []
            d = blog_obj.posts(blog_name, offset=offset)
            if SAVE_JSON:
                save_json.save(d)
            log.info("offset: {n}".format(n=offset))
            for post in d.get('posts', []):
                if post["type"] == "photo":
                    li.append(post)
                #
            #
            extra = {
                'tumblr_blog_name': blog_name,
                'offset': offset,
            }
            for url in extract_photo_urls(li):
                urls.append(ImageWithExtraInfo(url, extra))
            percent = round(len(urls) * 100 / cfg.TUMBLR_OFFSET)
            if statusbar:
                statusbar.progressbar.show()
                statusbar.progressbar.setValue(percent)
                # statusbar.flash_message(blue(f"{percent} %"))
                # without this nothing appeared until 100%:
                QApplication.processEvents()    # reason: https://stackoverflow.com/a/29917237/232485
            if len(urls) >= cfg.TUMBLR_OFFSET:
                break
            offset += cfg.TUMBLR_OFFSET
        # endwhile
        return urls
    except Exception as e:
        log.warning(f"exception: {str(e)}")
        log.warning(f"problem with tumblr blog '{blog_name}'")
        return []
    finally:
        if statusbar:
            statusbar.progressbar.hide()
        if mainWindow:
            mainWindow.loading_line.hide()
