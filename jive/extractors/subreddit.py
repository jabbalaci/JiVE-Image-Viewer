import os
import re
from http.cookiejar import MozillaCookieJar
from pathlib import Path
from time import sleep
from typing import List, Optional

import requests  # normal requests, unchanged
from curl_cffi import requests as cffi_requests
from curl_cffi.requests import Response as CffiResponse
from curl_cffi.requests.exceptions import RequestException as CffiRequestException
from PyQt5.QtWidgets import QApplication

from jive import config as cfg
from jive.extractors import imgur, tumblr
from jive.imagewithextra import ImageWithExtraInfo

log = cfg.log

url_template = "https://www.reddit.com/r/{subreddit}/.json"

url_template_with_after_id = (
    "https://www.reddit.com/r/{subreddit}/.json?after={after_id}"
)


def get_subreddit_name(text: str) -> Optional[str]:
    # with examples
    #
    # earthporn
    if "/" not in text:
        return text
    # /r/earthporn
    m = re.search(r"/r/([^/]*)", text)
    if m:
        return m.group(1)
    # https://www.reddit.com/r/EarthPorn/
    # https://reddit.com/r/EarthPorn/
    m = re.search(r"https?://(?:www\.)?reddit\.com/r/([^/]*)", text)
    if m:
        return m.group(1)
    # else
    return None


# We use curl_cffi instead of requests. reddit.com blocked connections via requests.
def get_connection(url: str, retries: int = 10, delay: float = 0.2) -> CffiResponse:
    cookies_txt = str(Path(cfg.BASE_DIR, "cookies.txt"))

    context = {
        "timeout": cfg.REQUESTS_TIMEOUT,
        "impersonate": "firefox",
    }

    if os.path.isfile(cookies_txt):
        log.info("cookies.txt was found")
        jar = MozillaCookieJar(cookies_txt)
        jar.load(ignore_expires=True, ignore_discard=True)
        context["cookies"] = jar
    else:
        log.info("cookies.txt is missing")

    r = None
    for attempt in range(retries):
        try:
            r = cffi_requests.get(url, **context)
            if r.status_code == 200:
                return r
            log.info(f"Attempt {attempt + 1}: status {r.status_code}")
        except CffiRequestException as e:
            log.info(f"Attempt {attempt + 1} failed: {e}")
        sleep(delay)

    if r is None:
        raise ConnectionError(f"All {retries} attempts failed for {url}")

    # log.info(f"Connection status code: {r.status_code}")
    return r


def read_subreddit(
    subreddit, after_id: Optional[str] = None, statusbar=None, mainWindow=None
) -> List[ImageWithExtraInfo]:
    try:
        if mainWindow:
            mainWindow.loading_line.show()
        if not after_id:
            img_url = url_template.format(subreddit=subreddit)
        else:
            img_url = url_template_with_after_id.format(
                subreddit=subreddit, after_id=after_id
            )
        # r = requests.get(img_url, headers=cfg.headers, timeout=cfg.REQUESTS_TIMEOUT)
        r = get_connection(img_url)
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
                QApplication.processEvents()  # reason: https://stackoverflow.com/a/29917237/232485
            entry = child["data"]
            domain = entry["domain"]
            link = entry["url"]
            after_id = entry[
                "name"
            ]  # use this for a new page that comes after this entry
            extra = {
                "subreddit": subreddit,
                "after_id": after_id,
                "next_page_url": f"https://www.reddit.com/r/{subreddit}/.json?after={after_id}",
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
                        img_url = link + ".jpg"  # it works sometimes
                        r = requests.head(
                            img_url, headers=cfg.headers, timeout=cfg.REQUESTS_TIMEOUT
                        )
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
