from functools import partial

import yaml
from PyQt5.QtWidgets import QAction, QMenu

from jive import config as cfg
from jive import mylogging as log

SORT = True
# SORT = False

class Categories:
    def __init__(self, parent, root_menu, open_subreddit_fn):
        self.parent = parent
        self.root_menu = root_menu
        self.open_subreddit_fn = open_subreddit_fn
        self.d = self.read()
        # pprint(self.d)

    def read(self):
        categories = cfg.categories_file()
        try:
            with open(categories) as f:
                log.info(f"{categories} was read")
                return yaml.safe_load(f)
        except:
            log.warning("couldn't read {0}".format(categories))
            return {}

    def _my_sorted(self, entries):
        """
        If SORT is True, then the categories AND the subreddit lists are sorted.
        The sorting is done in a case-insensitive mode.
        """
        return sorted(entries, key=str.lower) if SORT else entries

    def populate(self):
        for menu_name in self._my_sorted(self.d.keys()):
            subreddit_list = self.d[menu_name]
            menu = QMenu(self.root_menu)
            menu.setTitle(menu_name)
            self.root_menu.addMenu(menu)
            for subreddit in self._my_sorted(subreddit_list):
                act = QAction(subreddit, self.parent)
                act.triggered.connect(partial(self.open_subreddit_fn, subreddit, redraw=True))
                menu.addAction(act)
