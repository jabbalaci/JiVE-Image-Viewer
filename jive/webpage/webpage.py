#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin

from jive import config as cfg
from jive import helper
from jive.webpage.clustering import Cluster


# from jive import mylogging as log


def to_soup(html_source, parser='lxml'):
    return BeautifulSoup(html_source, parser)


def get_links_from_html(soup, base_url=None):
    """
    Get the links on a webpage. If the URL of the given
    page is provided in base_url, then links are absolute.

    The soup object is NOT modified.
    """
    li = []
    for tag in soup.findAll('a', href=True):
        if base_url:
            link = urljoin(base_url, tag['href'])
        else:
            link = tag['href']

        li.append(link)

    return li


def get_images_from_html(soup, base_url=None):
    """
    Get image src's on a webpage. If the URL of the given
    page is provided in base_url, then links are absolute.

    The soup object is NOT modified.
    """
    li = []
    for tag in soup.findAll('img', src=True):
        if base_url:
            link = urljoin(base_url, tag['src'])
        else:
            link = tag['src']

        li.append(link)

    return li


def filter_images(urls):
    return [url for url in urls if Path(url).suffix.lower() in cfg.SUPPORTED_FORMATS]


def extract(url, get_links=True, get_images=True):
    if get_links == False and get_images == False:
        return []
    # else
    r = requests.get(url, headers=cfg.headers, timeout=cfg.REQUESTS_TIMEOUT)
    soup = to_soup(r.text)
    lst = []
    if get_links:
        lst.extend(get_links_from_html(soup, base_url=url))
    if get_images:
        lst.extend(get_images_from_html(soup, base_url=url))
    lst = filter_images(lst)
    lst = helper.remove_duplicates(lst)

    return lst


def process(lst, sorting=False, clustering=False, distance=10):
    if sorting:
        lst = sorted(lst)
    if clustering:
        cl = Cluster()
        cl.clustering(lst, distance)
        # cl.show()
        # print("-" * 20)
        lst = cl.clusters['clusters']['largest']
        if sorting:
            lst = sorted(lst, key=lambda url: url.split('/')[-1])
    return lst


def get_four_variations(url, get_links=True, get_images=True, distance=10):
    # log.debug(f"url: {url}; get links: {get_links}; get images: {get_images}; distance: {distance}")

    urls = extract(url, get_links=get_links, get_images=get_images)

    lst1 = process(urls[:], sorting=False, clustering=False, distance=distance)
    lst2 = process(urls[:], sorting=False, clustering=True, distance=distance)
    lst3 = process(urls[:], sorting=True, clustering=False, distance=distance)
    lst4 = process(urls[:], sorting=True, clustering=True, distance=distance)

    return {
        1: lst1,
        2: lst2,
        3: lst3,
        4: lst4
    }
