import re
import sys

import imgurpython
from imgurpython import ImgurClient

from jive import config as cfg
from jive import mylogging as log

try:
    client = ImgurClient(cfg.IMGUR_CLIENT_ID, cfg.IMGUR_CLIENT_SECRET)
except:
    log.warning("missing or wrong imgur API keys")
    client = None


def is_album(url):
    return 'imgur.com' in url and ('/a/' in url or '/gallery/' in url)


def get_album_id(url):
    m = re.search(r'/(?:a|gallery)/([^/?#]+)', url)
    return m.group(1) if m else None


def extract_images_from_an_album(url):
    if client is None:
        log.warning(f"problem with your imgur API keys, cannot process {url}")
        return []
    #
    res = []
    album_id = get_album_id(url)
    if album_id:
        images = []
        try:
            images = client.get_album_images(album_id)
        except (imgurpython.helpers.error.ImgurClientError, TypeError):
            log.warning(f"problem with album {url}")
        except imgurpython.helpers.error.ImgurClientRateLimitError:
            log.warning("Imgur API: rate-limit exceeded", file=sys.stderr)

        res = [img.link for img in images]
    #
    return res
