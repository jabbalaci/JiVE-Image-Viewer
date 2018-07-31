from typing import Dict, Optional


class ImageWithExtraInfo:
    """
    In the first version the extractors returned a list of filenames (local case),
    or a list of URLs (remote case). However, if the URLs come from a subreddit
    for instance, then it'd be useful to assign extra info to an image, e.g.
    reddit ID, comments URL, image title, etc. Thus, extra is a dictionary that contains these
    additional pieces of information.
    """
    def __init__(self, fpath_or_url: str, extra_info: Optional[Dict[str, str]] = None) -> None:
        self.fpath_or_url = fpath_or_url    # file path or URL
        if extra_info is None:
            self.extra_info: Dict[str, str] = {}
        else:
            self.extra_info = extra_info