from typing import List

from jive.webpage import webpage


def is_imagefap_photo(url: str) -> bool:
    return "imagefap.com/photo/" in url


def get_urls(url: str) -> List[str]:
    variations = webpage.get_four_variations(url)
    result = [url for url in variations[1] if "/img/" not in url]
    return result