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
        print(f"{dname} doesn't exist")
        return
    #
    print(f"┌ start: remove {dname}")
    try:
        shutil.rmtree(dname)
    except:
        print("exception happened")
    print(f"└ end: remove {dname}")


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


def copy_dir(src, dest):
    print(f"┌ start: copy {src} -> {dest}")
    shutil.copytree(src, dest)
    print(f"└ end: copy {src} -> {dest}")


@task()
def clean():
    """Clean PyInstaller files and directories."""
    remove_file("start.spec")
    remove_directory("build")
    remove_directory("dist")


@task()
def clean_dist():
    remove_directory("dist/assets")
    remove_directory("dist/categories")


@task(clean_dist)
def exe():
    """Create executable with PyInstaller."""
    call_external_command("pyinstaller --onefile start.py")
    copy_dir("assets", "dist/assets")
    copy_dir("categories", "dist/categories")

