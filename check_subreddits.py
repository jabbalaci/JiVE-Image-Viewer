#!/usr/bin/env python3

"""
This is a tool to find dead (banned) subreddits in your categories file.
"""

from pprint import pprint
from time import sleep

import requests

from jive import config as cfg
from jive.categories import Categories

USER_AGENT = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0'}

TEMPLATE = "https://old.reddit.com/r/{0}"
TEMPLATE_JSON = "https://old.reddit.com/r/{0}/.json"


def wait() -> None:
    sleep(1.0)


def check(subreddits: list[str]) -> None:
    problematic = []
    for sr in subreddits:
        url = TEMPLATE_JSON.format(sr)
        print('#', url, flush=True)
        r = requests.get(url, headers=USER_AGENT)
        d = r.json()
        # pprint(d)
        if "error" in d and d['error'] == 404:
            problematic.append(sr)
            print("# !!!", flush=True)
        #
        wait()
    #
    print("---")
    for sr in problematic:
        print(sr)
    print("---")
    for sr in problematic:
        print(TEMPLATE.format(sr))


def main() -> None:
    d = Categories.read()
    subreddits = []
    for section in d:
        subreddits.extend(d[section])
    #
    subreddits = sorted(set(subreddits))

    check(subreddits)

##############################################################################

if __name__ == "__main__":
    main()
