import re
from pathlib import Path

import requests
from PyQt5.QtWidgets import QApplication

from jive import config as cfg
from jive import mylogging as log
from jive.extractors import imgur, tumblr
from jive.helper import blue

url_template = "https://www.reddit.com/r/{subreddit}/.json"


def get_subreddit_name(text):
    # with examples
    #
    # earthporn
    if '/' not in text:
        return text
    # /r/earthporn
    m = re.search(r'/r/([^/]*)', text)
    if m:
        return m.group(1)
    # https://www.reddit.com/r/EarthPorn/
    # https://reddit.com/r/EarthPorn/
    m = re.search(r'https?://(?:www\.)?reddit\.com/r/([^/]*)', text)
    if m:
        return m.group(1)
    # else
    return None


def read_subreddit(subreddit, statusbar=None):
    try:
        img_url = url_template.format(subreddit=subreddit)
        r = requests.get(img_url, headers=cfg.headers)
        d = r.json()
        res = []
        total = len(d["data"]["children"])
        for idx, child in enumerate(d["data"]["children"], start=1):
            percent = round(idx * 100 / total)
            log.info(f"{percent} %")
            if statusbar:
                statusbar.progressbar.show()
                statusbar.progressbar.setValue(percent)
                # statusbar.flash_message(blue(f"{percent} %"))
                # without this nothing appeared until 100%:
                QApplication.processEvents()    # reason: https://stackoverflow.com/a/29917237/232485
            entry = child["data"]
            domain = entry["domain"]
            link = entry["url"]
            if Path(link).suffix.lower() in cfg.SUPPORTED_FORMATS:
                res.append(link)
                continue
            #
            if domain.endswith(".tumblr.com"):
                # print("# tumblr found:", link)
                try:
                    images = tumblr.extract_images_from_a_specific_post(link)
                except:
                    log.warning(f"cannot extract images from {link}")
                    images = []
                # print("# extracted images:", len(images))
                for img_url in images:
                    if Path(img_url).suffix.lower() in cfg.SUPPORTED_FORMATS:
                        res.append(img_url)
                    #
                #
                continue
            # end tumblr section
            if domain.endswith("imgur.com"):
                if imgur.is_album(link):
                    try:
                        images = imgur.extract_images_from_an_album(link)
                    except:
                        log.warning(f"cannot extract images from {link}")
                        images = []
                    for img_url in images:
                        if Path(img_url).suffix.lower() in cfg.SUPPORTED_FORMATS:
                            res.append(img_url)
                        #
                    #
                else:
                    # it's on imgur.com but it's not an album
                    # it may be a single image embedded in an HTML page
                    try:
                        img_url = link + ".jpg"    # it works sometimes
                        r = requests.head(img_url, headers=cfg.headers)
                        if r.ok:
                            res.append(img_url)
                    except:
                        log.warning(f"problem with {link} -> {url}")
            # end imgur section
        #
        return res
    except KeyError:
        log.warning(f"cannot extract data from {img_url}")
        return []
    except:
        log.warning(f"problem with {img_url}")
        return []
    finally:
        if statusbar:
            statusbar.progressbar.hide()