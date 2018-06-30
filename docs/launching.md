Launching the application
=========================

During the installation pipenv automatically created a virtual
environment for the project. However, for launching the application,
you don't need to activate it manually every time.

Linux
-----

Enter the project directory and launch `caller.sh`. It'll
launch the application in its virt. env.

Windows
-------

Enter the project directory and launch `start.bat`.

Launching the application from anywhere
=======================================

In the previous we saw how to launch the application from
the project directory. But what if you want to launch it
from a different folder? How can you call JiVE from anywhere?

Linux
-----

In the folder `launchers`, you can find a launcher script called `jive`.
Copy it to a folder that is in your PATH.

Tip: in my HOME folder I have a subdirectory called `bin` that is in my PATH.
Thus, I copied `jive` to `~/bin`.

The content of `jive` is just one line:
```
~/Dropbox/python/JiVE-Image-Viewer/caller.sh "$@"
```

Customize the path of `caller.sh` in this file if your project
directory is located somewhere else.

Then, launching JiVE is trivial:
```
$ jive
```

Windows
-------

In the folder `launchers`, you can find a launcher script called `jive.bat`.
Copy it to a folder that is in your PATH.

The content of `jive.bat` is just a few lines:
```
cd C:\Dropbox\python\JiVE-Image-Viewer

pipenv run python start.py %1
```

Customize the path of the project folder in the first line.

Then, launching JiVE is trivial:
```
$ jive.bat
```

Tips
----

If you get the annoying "Open File - Security Warning" on `.bat` files, here is
how to disable it:

https://appuals.com/how-to-disable-open-file-security-warning-in-windows-7/
