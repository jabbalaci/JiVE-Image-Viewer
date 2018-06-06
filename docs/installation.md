Installation
============

JiVE is still a work in progress, but it's already usable. At the
moment I only provide the source code that you need to install
manually.

Requirements
------------

The application requires Python 3.6+.

Linux
-----

* download the source code
* create a virtual environment
* activate the virtual environment and install the necessary packages from `requirements.txt`
* start the app. with `start.py`

Windows
-------

For Windows users, here is a slightly more detailed list of instructions.

* install Python 3.6 to `C:\python36`
* make sure that the commands `python` and `pip` work in the shell
* download the source code and extract it to a dedicated folder
* Start the shell (e.g. `cmd`) and enter the project directory.
  From now on, every shell command must be executed in the project directory.
* in the shell:
```
$ pip install virtualenv
```
* create the directory `C:\temp\virtualenvs\jive`
* in the shell (and in the project directory):
```
$ virtualenv C:\temp\virtualenvs\jive
$ C:\temp\virtualenvs\jive\scripts\activate.bat
(jive)$ pip install -r requirements.txt
```
* test if the app. starts:
```
    (jive)$ python start.py
```
