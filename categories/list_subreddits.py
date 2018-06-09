#!/usr/bin/env python3

import sys
import webbrowser
from pprint import pprint
from time import sleep

import yaml

# REDDIT_URL = "www.reddit.com"    # new
REDDIT_URL = "old.reddit.com"    # old


def process(fname):
    with open(fname) as f:
        dataMap = yaml.safe_load(f)
    #
    # pprint(dataMap)
    # return
    for key, value in dataMap.items():
        for subreddit in value:
            url = f"https://{REDDIT_URL}/r/{subreddit}"
            print(url)
            # webbrowser.open_new_tab(url)
            # sleep(5)

##############################################################################

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: {0} input.yaml".format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)
    # else
    process(sys.argv[1])
