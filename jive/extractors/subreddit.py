import re
import requests
from PyQt5.QtWidgets import QApplication
from pathlib import Path
from typing import Optional, List

from jive import config as cfg
from jive.extractors import imgur, tumblr
from jive.imagewithextra import ImageWithExtraInfo

log = cfg.log

url_template = "https://www.reddit.com/r/{subreddit}/.json"

url_template_with_after_id = "https://www.reddit.com/r/{subreddit}/.json?after={after_id}"


def get_subreddit_name(text: str) -> Optional[str]:
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


def read_subreddit(subreddit, after_id: Optional[str] = None, statusbar=None, mainWindow=None) -> List[ImageWithExtraInfo]:
    try:
        if mainWindow:
            mainWindow.loading_line.show()
        if not after_id:
            img_url = url_template.format(subreddit=subreddit)
        else:
            img_url = url_template_with_after_id.format(subreddit=subreddit, after_id=after_id)
        r = requests.get(img_url, headers=cfg.headers, timeout=cfg.REQUESTS_TIMEOUT)
        d = r.json()
        result = []
        total = len(d["data"]["children"])
        for idx, child in enumerate(d["data"]["children"], start=1):
            percent = round(idx * 100 / total)
            log.info(f"{percent}%")
            if statusbar:
                statusbar.progressbar.show()
                statusbar.progressbar.setValue(percent)
                # statusbar.flash_message(blue(f"{percent} %"))
                # without this nothing appeared until 100%:
                QApplication.processEvents()    # reason: https://stackoverflow.com/a/29917237/232485
            entry = child["data"]
            domain = entry["domain"]
            link = entry["url"]
            after_id = entry["name"]    # use this for a new page that comes after this entry
            extra = {
                'subreddit': subreddit,
                'after_id': after_id,
                'next_page_url': f'https://www.reddit.com/r/{subreddit}/.json?after={after_id}'
            }
            if Path(link).suffix.lower() in cfg.SUPPORTED_FORMATS:
                result.append(ImageWithExtraInfo(link, extra))
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
                        result.append(ImageWithExtraInfo(img_url, extra))
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
                            result.append(ImageWithExtraInfo(img_url, extra))
                        #
                    #
                else:
                    # it's on imgur.com but it's not an album
                    # it may be a single image embedded in an HTML page
                    try:
                        img_url = link + ".jpg"    # it works sometimes
                        r = requests.head(img_url, headers=cfg.headers, timeout=cfg.REQUESTS_TIMEOUT)
                        if r.ok:
                            result.append(ImageWithExtraInfo(img_url, extra))
                    except:
                        log.warning(f"problem with {link} -> {img_url}")
            # end imgur section
        #
        return result
    except KeyError:
        log.warning(f"cannot extract data from {img_url}")
        return []
    except Exception as e:
        log.warning(f"exception: {str(e)}")
        log.warning(f"problem with {img_url}")
        return []
    finally:
        if statusbar:
            statusbar.progressbar.hide()
        if mainWindow:
            mainWindow.loading_line.hide()