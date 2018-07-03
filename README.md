JiVE (Jabba's Image Viewer)
===========================

A general purpose, cross-platform image viewer with some built-in NSFW support, written in Python 3.6 using PyQt5.
A unique feature of JiVE is that it allows you to browse online images just as if they were local images. JiVE
is tested under Linux and Windows.

This is a work in progress... but it's already usable.

Table of Contents
-----------------

* [Motivation](docs/motivation.md)
* [Installation](docs/installation.md)
* [Launching the application](docs/launching.md)
* [First steps after installation (API keys)](docs/first_steps.md)
* [NSFW support](docs/nsfw.md)
* [How to use the app?](docs/usage.md)
* [Open the images of an arbitrary webpage](docs/webpage.md)
* [Marking images (save, wallpaper, delete)](docs/marking.md)
* [Find duplicates](docs/duplicates.md)
* [Browsing a subreddit](docs/browsing_subreddit.md)
* [Sequence URL](docs/sequence_url.md)
* [Preferences](docs/preferences.md)
* [Command-line arguments](docs/command_line.md)
* [[dev] Local settings](docs/settings.md)
* [[dev] caching](docs/cache.md)
* [Logging](docs/logging.md)
* [FAQ](docs/faq.md)

Screenshots
-----------

In action:

<p align="center">
  <img width="60%" src="assets/screenshots/screenshot.jpg">
</p>

Selecting an NSFW subreddit:

<p align="center">
  <img width="60%" src="assets/screenshots/nsfw.png">
</p>

The subreddits are read from a config file (`categories/categories.yaml`), so feel free to edit and extend
this file with your favourite subreddits...
