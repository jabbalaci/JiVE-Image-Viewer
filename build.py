#!/usr/bin/env python3

"""
pynt's build file
https://github.com/rags/pynt

Usage:

$ pynt
"""

import os
import shutil
import sys
from pathlib import Path

from pynt import task


def remove_file(fname):
    if not os.path.exists(fname):
        print(f"{fname} doesn't exist")
        return
    #
    print(f"┌ start: remove {fname}")
    try:
        os.remove(fname)
    except:
        print("exception happened")
    print(f"└ end: remove {fname}")


def remove_directory(dname):
    if not os.path.exists(dname):
        print(f"{pretty(dname, True)} doesn't exist")
        return
    #
    print(f"┌ start: remove {pretty(dname)}")
    try:
        shutil.rmtree(dname)
    except:
        print("exception happened")
    print(f"└ end: remove {pretty(dname)}")


def call_external_command(cmd):
    print(f"┌ start: calling external command '{cmd}'")
    os.system(cmd)
    print(f"└ end: calling external command '{cmd}'")


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def pretty(name, force=False):
    """
    If name is a directory, then add a trailing slash to it.
    """
    if name.endswith("/"):
        return name    # nothing to do
    # else
    if force:
        return f"{name}/"
    # else
    if not os.path.isdir(name):
        return name    # not a dir. => don't modify it
    # else
    return f"{name}/"


def copy_dir(src, dest):
    print(f"┌ start: copy {pretty(src)} -> {pretty(dest)}")
    shutil.copytree(src, dest)
    print(f"└ end: copy {pretty(src)} -> {pretty(dest)}")


def copy_file(src, dest):
    p = Path(dest)
    if not p.exists():
        p.mkdir(parents=True)
    print(f"┌ start: copy {src} -> {pretty(dest)}")
    shutil.copy(src, dest)
    print(f"└ end: copy {src} -> {pretty(dest)}")

###########
## Tasks ##
###########

@task()
def clean():
    """clean PyInstaller files and directories"""
    remove_file("start.spec")
    remove_directory("build")
    remove_directory("dist")


@task()
def clean_dist():
    """delete the folders `dist/assets` and `dist/categories`"""
    remove_directory("dist/assets")
    remove_directory("dist/categories")


@task(clean_dist)
def exe():
    """create executable with PyInstaller"""
    call_external_command("pyinstaller --onefile start.py")
    copy_dir("assets", "dist/assets")
    remove_directory("dist/assets/screenshots")
    copy_file("categories/categories.yaml", "dist/categories")
    copy_file("tools/verify_your_api_keys.py", "dist/tools")
    copy_file("preferences.ini", "dist/")

