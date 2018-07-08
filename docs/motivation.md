Motivation
==========

When I started to learn Python, I worked on an image viewer
application called [HenWer](https://github.com/jabbalaci/HenWer).
I found an open-source image viewer, [ManWer](https://code.google.com/archive/p/manwer/),
and I extended it with some extra functionalities. As a Python newbie
back then, I enjoyed working on it very much.

Now, several years later, I wanted to use HenWer again. However,
it was written in Python 2 with wxPython. I could make it run,
but some features stopped working (e.g. zooming). It was also
a bit complicated to install wxPython properly.

So, I decided to write a new image viewer (called JiVE) from scratch using
modern technologies like Python 3 and PyQt5. HenWer had some
cool features that I took over and I also added
several new functionalities.

JiVE is designed to be cross-platform. It is tested under Linux
and Windows. I couldn't try it on Mac, but it should work on that
platform too.

A unique feature of JiVE is that it allows you to browse
online images just as if they were local images. We can say
that online images are first-class citizens. For instance,
you can provide the name of a subreddit. JiVE extracts all the images
from the subreddit and then you can browse among them with the arrow keys.
Local and online images are handled the same way.
