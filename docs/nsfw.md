NSFW support
============

JiVE is a general purpose, cross-platform image viewer,
but it has some unique built-in NSFW support.

Namely, it can extract images from an arbitrary subreddit
on [reddit.com](https://www.reddit.com). In addition,
if a reddit post points on an Imgur album/gallery or
on a Tumblr post, JiVE follows the link and extracts
those images too.

JiVE includes a small hierarchy of some selected NSFW subreddits.
Where to find it: *right click* -> *Select subreddit...*

Create your own categories
--------------------------

The subreddit hierarchy in the menu is built from a config file
(`categories/categories.yaml`). Just open this file in your
favourite text editor and modify / extend the list. After saving
the file, you don't need to restart JiVE. It's enough to reset it
(*File* -> *Reset* or *Ctrl + Alt +R*), and the menu will reflect your
changes.

Can I add SFW subreddits too?
-----------------------------

Of course :) Nothing will stop you. Actually, the current list
also has some SFW subreddits, but currently they are ridiculously
under-represented.

Where can I find more NSFW subreddits?
--------------------------------------

You'll have to do some research. This list can be a good
starting point: [http://redditlist.com/nsfw](http://redditlist.com/nsfw).
