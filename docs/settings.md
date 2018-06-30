[dev] Local settings
====================

(*If a section is prefixed with "[dev]" (like this section),*
*its intended audience is developers who want to contribute*
*to the project.*

*If you just want to use JiVE, you can skip the [dev] sections.*)

JiVE creates a local settings file. This file
is updated every time you close the application.

You can find out the location of this file if you go
to *View* -> *Important files and folders*. Check out
the location of `settings.json`.

Normally you don't need to do anything with this file. JiVE
will read it upon start and write to it upon close.

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
