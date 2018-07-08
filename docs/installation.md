Installation
============

If you want to try the latest version, you need to
download the source code and install it manually.

Requirements
------------

The application requires Python 3.6+. As for the package manager,
I chose [pipenv](https://github.com/pypa/pipenv) for its simplicity.

Pipenv
------

Under **Windows** you can install pipenv the following way:
* open a terminal (`cmd`)
* `pip install pipenv`
* then run `pipenv` in the terminal to be sure that it works

Under **Linux** you can install it globally (`sudo pip install pipenv`)
or locally (`pip install pipenv --user`). I have a blog
post about the local installation [here](https://pythonadventures.wordpress.com/2018/06/29/pip-install-user/).
I suggest a local installation. When the installation is done,
execute the command `pipenv` in the terminal to be sure that it works.

Linux
-----

* download the source code to a dedicated folder
* enter the project's folder and issue the command `pipenv install`
* If you want to install the development packages too, use the
  command `pipenv install --dev`. If you just want to use JiVE,
  the dev. packages are not necessary.
* If you install the dev. packages, you'll get a warning message
  that `pywin32` couldn't be
  installed. You can ignore it. The package `pyinstaller`
  has this dependency under Windows but it doesn't exist for
  Linux. Just ignore it.
* Activate the virtual environment (pipenv created one for you) with
  `pipenv shell` (or simply launch `./activate`, which does the same thing).
  Note that pipenv will start a sub-shell! If you want to
  deactivate the virt. env., simply quit the sub-shell with `exit`.
* start the app. with `./start.py`

If you want to launch the app. without activating the virt.
env. first, launch `caller.sh`.

Windows
-------

The process is very similar to Linux:

* you'll need Python 3.6+
* make sure that the commands `python` and `pipenv` work in the shell
* download the source code to a dedicated folder
* In the shell, enter the project's folder and issue the command `pipenv install`.
  Prepare that it'll take several minutes...
* If you want to install the development packages too, use the
  command `pipenv install --dev`. If you just want to use JiVE,
  the dev. packages are not necessary.
* Activate the virtual environment (pipenv created one for you) with
  `pipenv shell` (or simply launch `activate.bat`, which does the same thing).
  Note that pipenv will start a sub-shell! If you want to
  deactivate the virt. env., simply quit the sub-shell with `exit`.
* start the app. with `python start.py`

If you want to launch the app. without activating the virt.
env. first, launch `start.bat`.
