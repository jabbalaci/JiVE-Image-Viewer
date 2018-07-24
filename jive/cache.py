import sys
from collections import deque

from pathlib import Path
from typing import Dict

from jive import helper
from jive import mylogging as log


class CacheElem:
    def __init__(self, path_obj: Path) -> None:
        self.p = path_obj
        self.name = str(path_obj)
        self.stat = path_obj.stat()
        self.mtime = self.stat.st_mtime
        self.size = self.stat.st_size    # file size in bytes


class CacheQueue:
    def __init__(self, cache_dir: str, max_size_bytes: int) -> None:
        self.cache_dir = cache_dir
        self.max_size_bytes = max_size_bytes    # size limit of the cache folder
        self.q: deque = deque()
        self.size = 0

        self.read_cache_dir()

    def read_cache_dir(self) -> None:
        for entry in sorted(Path(self.cache_dir).iterdir(), key=lambda f: f.stat().st_mtime):
            elem = CacheElem(entry)
            self.add_elem(elem, verbose=False)

    def add_elem(self, elem: CacheElem, verbose: bool = True) -> None:
        self.q.append(elem)
        self.size += elem.size
        # if verbose:
        #     log.debug(f"cache news: {elem.name} was added")

    def remove_elem(self) -> None:
        first = self.q.popleft()
        first.p.unlink()
        if not first.p.exists():
            self.size -= first.size
            # log.debug(f"cache news: {first.name} was deleted")
        else:
            log.warning(f"cache news: couldn't remove {first.name}")

    def shrink(self) -> None:
        # if we are below the threshold => OK, nothing to do
        if self.size <= self.max_size_bytes:
            return
        # else, if the cache folder's size is over the limit
        while True:
            if self.size <= self.max_size_bytes:
                break
            if len(self.q) == 1:
                log.warning("the cache folder grew too big but it has just one element")
                log.warning("Tip: increase the cache size, the current value is too small.")
                break
            self.remove_elem()

    # def get_size(self):
    #     return self.size

    def debug(self) -> None:
        num = helper.pretty_num(len(self.q))
        log.debug(f"number of images in the cache: {num}")
        size = helper.pretty_num(self.size)
        log.debug(f"cache size in bytes: {size}")


class Cache:
    def __init__(self, options: Dict[str, str], cache_dir: str) -> None:
        self.use_cache: bool = True if options.get("use_cache", "") == "yes" else False
        self.cache_dir = cache_dir

        # if the cache is disabled, then stop here
        if not self.use_cache:
            return

        self.cache_size_bytes = self._read_cache_size(options)

        self.queue = CacheQueue(self.cache_dir, self.cache_size_bytes)
        self.queue.debug()

        self.shrink()

    def enabled(self) -> bool:
        return self.use_cache

    def __contains__(self, url: str) -> bool:
        """
        In order to use the 'in' operator.
        Return True, if the image (given by its url) is in the cache. Otherwise, return False.
        """
        md5_hash = helper.string_to_md5(url)
        p = Path(self.cache_dir, md5_hash)
        return p.is_file()

    def get_fname_to_url(self, url: str) -> str:
        md5_hash = helper.string_to_md5(url)
        p = Path(self.cache_dir, md5_hash)
        return str(p)

    def save(self, url: str, binary_data: bytes) -> None:
        if len(binary_data) == 0:    # It happened that the status code was forbidden (403), and it
            return                   # created an empty file in the cache. This is here to prevent that.

        fname = self.get_fname_to_url(url)
        with open(fname, 'wb') as f:
            f.write(binary_data)
        #
        self.add_to_queue(fname)
        self.shrink()
        # self.queue.debug()

    def add_to_queue(self, fname: str) -> None:
        p = Path(fname)
        elem = CacheElem(p)
        self.queue.add_elem(elem)

    def shrink(self) -> None:
        """
        If the cache folder's size is over the limit, then remove old entries.
        Goal: go below the size threshold.
        If the size of the cache is below the limit, then shrink() does nothing.
        """
        self.queue.shrink()

    def _read_cache_size(self, options: Dict[str, str]) -> int:
        try:
            mb = int(options.get("cache_size_mb", "0"))
        except:
            mb = 0

        if mb < 20:
            log.error(f"the cache size should be at least 20 MB")
            log.error(f"Tip: disable cache completely or increase the cache size.")
            sys.exit(1)

        # size in bytes (for simplicity, we multiply by 1,000 instead of 1,024)
        return mb * 1_000 * 1_000