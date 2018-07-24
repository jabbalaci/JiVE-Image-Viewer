from typing import Dict

class Shortcuts:
    def __init__(self) -> None:
        self.window_shortcuts: Dict = {}
        self.menubar_actions: Dict = {}

    def _normalize(self, key: str) -> str:
        return key.upper().replace(" ", "")

    def register_window_shortcut(self, key: str, q_shortcut, connect_function) -> None:
        key = self._normalize(key)
        self.window_shortcuts[key] = q_shortcut
        q_shortcut.activated.connect(connect_function)

    def register_menubar_action(self, key: str, q_action, connect_function) -> None:
        key = self._normalize(key)
        self.menubar_actions[key] = q_action
        q_action.setShortcut(key)
        q_action.triggered.connect(connect_function)

    def enable_all_window_shortcuts(self) -> None:
        for shortcut in self.window_shortcuts.values():
            shortcut.setEnabled(True)

    def disable_conflicting_window_shortcuts(self) -> None:
        for key in self.menubar_actions:
            if key in self.window_shortcuts:
                self.window_shortcuts[key].setEnabled(False)
