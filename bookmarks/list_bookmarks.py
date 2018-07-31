#!/usr/bin/env python3

import sys
import webbrowser
from pprint import pprint
from time import sleep
import re

import yaml


def process(fname):
    with open(fname) as f:
        dataMap = yaml.safe_load(f)
    #
    # pprint(dataMap)
    # return

    for key, value in dataMap.items():
        for url in value:
            # print(url)
            m = re.search(r"\[(.*)\]\((.*)\)", url)
            if m:
                description = m.group(1)
                link = m.group(2)
                print(f"{description} -> {link}")

##############################################################################

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: {0} input.yaml".format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)
    # else
    process(sys.argv[1])
