Preparation
===========

* install Python 3.6 to `C:\python36`
* make sure that the commands `python` and `pip` work in the shell
* in the shell:

    $ pip install virtualenv
* create the directory `C:\temp\virtualenvs\jive`
* in the shell:

    $ virtualenv C:\temp\virtualenvs\jive
    $ C:\temp\virtualenvs\jive\scripts\activate.bat
    (jive)$ pip install -r requirements.txt
* test if the app. starts:

    (jive)$ python start.py

Start the app.
==============

There is no need to activate the virt. environment.
Just launch `start.bat`.

Tips
====

If you get the annoying "Open File - Security Warning" on `start.bat`, here is
how to disable it:

https://appuals.com/how-to-disable-open-file-security-warning-in-windows-7/
