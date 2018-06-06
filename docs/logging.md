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
$ ./start.py
INFO  2018-06-06 18:48:26 config.<module>() [27]: RELEASE version
INFO  2018-06-06 18:48:26 config.<module>() [48]: using /media/DATA/Dropbox/python/JiVE-Image-Viewer/categories/categories.yaml
INFO  2018-06-06 18:48:26 settings.read() [29]: /home/jabba/.local/share/JiveImageViewer/settings.json was read
INFO  2018-06-06 18:48:28 settings.write() [46]: /home/jabba/.local/share/JiveImageViewer/settings.json was written
```
