import re
import yaml
from PyQt5.QtWidgets import QAction, QMenu
from functools import partial
from typing import Dict, List, KeysView, Union, Optional
from typing import Tuple

from jive import config as cfg

log = cfg.log

# SORT = True
SORT = False


class Bookmarks:
    def __init__(self, parent, root_menu, open_new_browser_tab_fn) -> None:
        self.parent = parent
        self.root_menu = root_menu
        self.open_new_browser_tab_fn = open_new_browser_tab_fn
        self.d = self.read()
        # pprint(self.d)

    @staticmethod
    def read() -> Dict[str, List[str]]:
        bookmarks = cfg.bookmarks_file()
        try:
            with open(bookmarks) as f:
                log.info(f"{bookmarks} was read")
                result: Dict[str, List[str]] = yaml.safe_load(f)
                return result
        except Exception as e:
            log.warning("couldn't read {0}".format(bookmarks))
            log.warning(e)
            return {}

    @staticmethod
    def _my_sorted(entries: Union[KeysView[str], List[str]]) -> Union[KeysView[str], List[str]]:
        """
        If SORT is True, then the categories AND the subreddit lists are sorted.
        The sorting is done in a case-insensitive mode.
        """
        return sorted(entries, key=str.lower) if SORT else entries

    @staticmethod
    def extract_parts(entry: str) -> Optional[Tuple[str, str]]:
        m = re.search(r"\[(.*)\]\((.*)\)", entry)
        if m:
            description = m.group(1)
            link = m.group(2)
            return description, link
        else:
            return None

    def populate(self) -> None:
        for category_name in self._my_sorted(self.d.keys()):
            url_list = self.d[category_name]
            menu = QMenu(self.root_menu)
            menu.setToolTipsVisible(True)
            menu.setTitle(category_name)
            self.root_menu.addMenu(menu)
            for entry in self._my_sorted(url_list):
                result = self.extract_parts(entry)
                if result:
                    description, link = result
                    act = QAction(description, self.parent)
                    act.setToolTip(link)
                    act.triggered.connect(partial(self.open_new_browser_tab_fn, link))
                    menu.addAction(act)
                else:
                    if re.search(r"^-{3,}$", entry):    # "---" (with length >= 3) is a separator
                        menu.addSeparator()
                    else:
                        log.warning(f"couldn't parse the bookmark line '{entry}'")
