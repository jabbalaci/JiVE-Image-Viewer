#!/usr/bin/env python3

"""
The NSFW website fuskator.com allows you to specify a sequence URL,
which is a compressed representation of a gallery's URLs.

How it works:

First Gallery Image: http://www.website.com/001.jpg
Last Gallery Image: http://www.website.com/030.jpg
Sequence: [001-030]
Sequence URL: http://www.website.com/[001-030].jpg

From the sequence URL we restore the complete list of URLs.
"""

import re
from typing import List

from jive import helper
from jive import mylogging as log


def is_valid_sequence_url(url: str, verbose: bool = False) -> bool:
    m = re.search("\[(.+?)-(.+?)\]", url)
    if not m:
        if verbose: log.warning(f"no sequence was found in {url}")
        return False
    # else
    return True


def get_urls_from_sequence_url(url: str) -> List[str]:
    if not is_valid_sequence_url(url):
        return []
    # else
    return helper.unfold_sequence_url(url)

##############################################################################

if __name__ == "__main__":
    url = "http://www.website.com/[001-030].jpg"    # for testing

    urls = get_urls_from_sequence_url(url)
    for url in urls:
        print(url)
