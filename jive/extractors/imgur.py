import sys

import imgurpython
import re
from imgurpython import ImgurClient
from typing import Optional, List

from jive import config as cfg

log = cfg.log

client = None


def connection() -> None:
    global client

    try:
        client = ImgurClient(cfg.IMGUR_CLIENT_ID, cfg.IMGUR_CLIENT_SECRET)
    except Exception as e:
        log.warning("missing or wrong imgur API keys")
        log.warning(f"imgur exception: {str(e)}")
        client = None


def is_album(url: str) -> bool:
    return 'imgur.com' in url and ('/a/' in url or '/gallery/' in url)


def get_album_id(url: str) -> Optional[str]:
    m = re.search(r'/(?:a|gallery)/([^/?#]+)', url)
    return m.group(1) if m else None


def extract_images_from_an_album(url: str) -> List[str]:
    if client is None:
        connection()

    # if it's still None
    if client is None:
        log.warning(f"problem with your imgur API keys, cannot process {url}")
        return []
    #
    result: List[str] = []
    album_id = get_album_id(url)
    if album_id:
        images = []
        try:
            images = client.get_album_images(album_id)
        except (imgurpython.helpers.error.ImgurClientError, TypeError):
            log.warning(f"problem with album {url}")
        except imgurpython.helpers.error.ImgurClientRateLimitError:
            log.warning("Imgur API: rate-limit exceeded", file=sys.stderr)

        result = [img.link for img in images]
    #
    return result
