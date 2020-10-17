import webbrowser
from PyQt5.QtWidgets import QMessageBox

from jive import config as cfg


def open_about(parent) -> None:
    text = f"""
<strong>Jabba's Image Viewer {cfg.VERSION}</strong>

<a href="https://github.com/jabbalaci/JiVE-Image-Viewer">https://github.com/jabbalaci/JiVE-Image-Viewer</a>

Laszlo Szathmary (Jabba Laci), 2018--2020
jabba.laci@gmail.com
""".strip().replace("\n", "<br>")
    QMessageBox.about(parent, "About", text)


def open_help() -> None:
    url = "https://github.com/jabbalaci/JiVE-Image-Viewer/blob/master/docs/usage.md"
    webbrowser.open_new_tab(url)
