Local settings
==============

JiVE creates a local settings file. This file
is updated every time you close the application.

To figure out the location of this file, execute the
file `tools/location_of_settings.py`. Here is my output:

Under Linux
-----------
```
$ ./location_of_settings.py
...
Your settings file is located here: /home/jabba/.local/share/JiveImageViewer/settings.json
```

Under Windows 10
----------------

Start `cmd` in the project directory.
```
$ activate.bat
(jive)$ cd tools
(jive)$ python location_of_settings.py
...
Your settings file is located here: C:\Users\Jabba Laci\AppData\Local\JiveImageViewer\settings.json
```

Content of the settings file
----------------------------

It saves values that you provided in the GUI last time. Thus, when you want to
open a directory again, for instance, the selector dialog will jump to the
same directory. Here is a sample:

```
{
  "last_file_opened": "/media/DATA/Dropbox/python/JiVE-Image-Viewer/samples/burned_man.jpg",
  "last_dir_opened": "",
  "last_open_url_auto_detect": "wallpapers"
}
```
