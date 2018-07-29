from typing import Optional

from jive import helper


def is_gallery(url: str) -> bool:
    valid = ("fuskator.com/full/", "fuskator.com/thumbs/")
    for part in valid:
        if part in url:
            return True
    #
    return False


def extract_embedded_url(url: str) -> Optional[str]:
    result = None
    soup = helper.get_page_as_soup(url)
    if soup:
        tag = soup.find('span', {'class': 'fn url'})
        if tag:
            result = tag.text
        #
    #
    return result