#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin

from jive import config as cfg
from jive import helper
from jive.webpage.clustering import Cluster

log = cfg.log


def to_soup(html_source: str, parser: str = 'lxml') -> BeautifulSoup:
    return BeautifulSoup(html_source, parser)


def get_links_from_html(soup: BeautifulSoup, base_url: Optional[str] = None) -> List[str]:
    """
    Get the links on a webpage. If the URL of the given
    page is provided in base_url, then links are absolute.

    The soup object is NOT modified.
    """
    result = []
    for tag in soup.findAll('a', href=True):
        if base_url:
            link = urljoin(base_url, tag['href'])
        else:
            link = tag['href']

        result.append(link)

    return result


def get_images_from_html(soup: BeautifulSoup, base_url: Optional[str] = None) -> List[str]:
    """
    Get image src's on a webpage. If the URL of the given
    page is provided in base_url, then links are absolute.

    The soup object is NOT modified.
    """
    result = []
    for tag in soup.findAll('img', src=True):
        if base_url:
            link = urljoin(base_url, tag['src'])
        else:
            link = tag['src']

        result.append(link)

    return result


def filter_images(urls: List[str]) -> List[str]:
    return [url for url in urls if Path(url).suffix.lower() in cfg.SUPPORTED_FORMATS]


def extract(url, get_links: bool = True, get_images: bool = True) -> List[str]:
    if (get_links == False) and (get_images == False):
        return []
    # else
    r = requests.get(url, headers=cfg.headers, timeout=cfg.REQUESTS_TIMEOUT)
    soup = to_soup(r.text)
    result = []
    if get_links:
        result.extend(get_links_from_html(soup, base_url=url))
    if get_images:
        result.extend(get_images_from_html(soup, base_url=url))
    result = filter_images(result)
    result = helper.remove_duplicates(result)

    return result


def process(lst: List[str], sorting: bool = False, clustering: bool = False, distance: int = 10) -> List[str]:
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


def get_four_variations(url: str, get_links: bool = True, get_images: bool = True, distance: int = 10) -> Dict[int, List[str]]:
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
