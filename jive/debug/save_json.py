from typing import Dict
import json
from pathlib import Path
import time

DIR = "/trash/tmp/tumblr_json_files"


def generate_fname() -> str:
    return str(time.time()).replace(".", "_") + ".json"


def save(d: Dict) -> None:
    fname = str(Path(DIR, generate_fname()))
    with open(fname, "w") as f:
        json.dump(d, f, indent=4)