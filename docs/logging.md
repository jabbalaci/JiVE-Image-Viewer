Logging
=======

The project is still under heavy development. I suggest starting it
from the command-line. There you will get a detailed log stream, thus
if there is any problem, it makes debugging easier.

In the log you can also find some useful information, e.g. location of
the settings file, location of the categories file, etc.

Example
-------
```
$ jive
INFO  2018-06-30 19:44:31 jive.check_api_keys() [1989]: tumblr API key was found
INFO  2018-06-30 19:44:31 jive.check_api_keys() [1997]: imgur API keys were found
INFO  2018-06-30 19:44:31 settings.read() [30]: /home/jabba/.local/share/JiveImageViewer/settings.json was read
INFO  2018-06-30 19:44:31 categories.read() [24]: /home/jabba/.local/share/JiveImageViewer/categories.yaml was read
DEBUG 2018-06-30 19:44:31 cache.debug() [67]: number of images in the cache: 232
DEBUG 2018-06-30 19:44:31 cache.debug() [69]: cache size in bytes: 99,681,981
INFO  2018-06-30 19:44:31 categories.read() [24]: /home/jabba/.local/share/JiveImageViewer/categories.yaml was read
```
