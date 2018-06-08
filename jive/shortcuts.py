class Shortcuts:
    def __init__(self):
        self.window_shortcuts = {}
        self.menubar_actions = {}

    def _normalize(self, key):
        return key.upper().replace(" ", "")

    def register_window_shortcut(self, key, q_shortcut, connect_function):
        key = self._normalize(key)
        self.window_shortcuts[key] = q_shortcut
        q_shortcut.activated.connect(connect_function)

    def register_menubar_action(self, key, q_action, connect_function):
        key = self._normalize(key)
        self.menubar_actions[key] = q_action
        q_action.setShortcut(key)
        q_action.triggered.connect(connect_function)

    def enable_all_window_shortcuts(self):
        for shortcut in self.window_shortcuts.values():
            shortcut.setEnabled(True)

    def disable_conflicting_window_shortcuts(self):
        for key in self.menubar_actions:
            if key in self.window_shortcuts:
                self.window_shortcuts[key].setEnabled(False)
