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

import mylogging as log


def is_valid_sequence_url(url):
    lst = re.findall("\[(.*?)-(.*?)\]", url)
    if len(lst) == 0:
        log.warning(f"no sequence was found in {url}")
        return False
    if len(lst) > 1:
        log.warning(f"several sequences were found in {url} , which is not supported")
        return False
    # else, if len(lst) == 1
    return True
        

def get_urls_from_sequence_url(url, statusbar=None):
    res = []

    if not is_valid_sequence_url(url):
        return []

    m = re.search("\[(.*?)-(.*?)\]", url)
    if m:
        start = m.group(1)
        end = m.group(2)

        prefix = url[:url.find('[')]
        postfix = url[url.find(']')+1:]

        zfill = start.startswith('0') or end.startswith('0')

        # print(url)
        # print(prefix)
        # print(postfix)

        if zfill and (len(start) != len(end)):
            log.warning(f"start and end sequences in {url} must have the same lengths if they are zero-filled")
            return []
        # else
        length = len(start)
        if start.isdigit() and end.isdigit():
            start = int(start)
            end = int(end)
            for i in range(start, end+1):
                middle = i
                if zfill:
                    middle = str(i).zfill(length)
                curr = f"{prefix}{middle}{postfix}"
                res.append(curr)
            # endfor
        # endif
    # endif

    return res

##############################################################################

if __name__ == "__main__":
    url = "http://www.website.com/[001-030].jpg"    # for testing
    
    urls = get_urls_from_sequence_url(url)
    for url in urls:
        print(url)
