import yaml
from PyQt5.QtWidgets import QAction, QMenu
from functools import partial
from typing import Dict, List, KeysView, Union
import random

from jive import config as cfg

log = cfg.log

SORT = True
# SORT = False

class Categories:
    def __init__(self, parent, root_menu, open_subreddit_fn) -> None:
        self.parent = parent
        self.root_menu = root_menu
        self.open_subreddit_fn = open_subreddit_fn
        self.d = self.read()
        # pprint(self.d)

    @staticmethod
    def read() -> Dict[str, List[str]]:
        categories = cfg.categories_file()
        try:
            with open(categories) as f:
                log.info(f"{categories} was read")
                result: Dict[str, List[str]] = yaml.safe_load(f)
                return result
        except Exception as e:
            log.warning("couldn't read {0}".format(categories))
            log.warning(e)
            return {}

    @staticmethod
    def _my_sorted(entries: Union[KeysView[str], List[str]]) -> Union[KeysView[str], List[str]]:
        """
        If SORT is True, then the categories AND the subreddit lists are sorted.
        The sorting is done in a case-insensitive mode.
        """
        return sorted(entries, key=str.lower) if SORT else entries

    def populate(self) -> None:
        for menu_name in self._my_sorted(self.d.keys()):
            subreddit_list = self.d[menu_name]
            menu = QMenu(self.root_menu)
            menu.setTitle(menu_name)
            self.root_menu.addMenu(menu)
            for subreddit in self._my_sorted(subreddit_list):
                act = QAction(subreddit, self.parent)
                act.triggered.connect(partial(self.open_subreddit_fn, subreddit))
                menu.addAction(act)

    @staticmethod
    def get_subreddits() -> List[str]:
        collect = []
        d = Categories.read()
        for k, v in d.items():
            collect.extend(v)
        return collect

    @staticmethod
    def get_random_subreddit() -> str:
        return random.choice(Categories.get_subreddits())