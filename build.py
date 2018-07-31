#!/usr/bin/env python3

"""
pynt's build file
https://github.com/rags/pynt

Usage:

$ pynt
"""

import os
import shlex
import shutil
import sys
from pathlib import Path
from subprocess import PIPE, Popen

from pynt import task

def get_platform():
    text = sys.platform
    if text.startswith("linux"):
        return "linux"
    if text.startswith("win"):
        return "windows"
    # else
    raise RuntimeError("unknown platform")

platform = get_platform()


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


def call_popen_with_env(cmd, env):
    print(f"┌ start: calling Popen with '{cmd}' in a custom environment")
    p = Popen(shlex.split(cmd), env=env)
    p.communicate()
    print(f"└ end: calling Popen with '{cmd}' in a custom environment")


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


def rename_file(src, dest):
    print(f"┌ start: rename {src} -> {dest}")
    shutil.move(src, dest)
    print(f"└ end: rename {src} -> {dest}")


def compile_ui_file(in_file, out_file):
    prg = "pyuic5"    # for Linux
    cmd = f"{prg} {in_file} -o {out_file}"
    print(f"┌ start: compile {in_file} -> {out_file}")
    os.system(cmd)
    print(f"└ end: compile {in_file} -> {out_file}")


def compile_rc_file(in_file, out_file):
    prg = "pyrcc5"    # for Linux
    cmd = f"{prg} {in_file} -o {out_file}"
    print(f"┌ start: compile {in_file} -> {out_file}")
    os.system(cmd)
    print(f"└ end: compile {in_file} -> {out_file}")


def verify_config_file(exe_or_tests):
    with open("jive/config.py") as f:
        lines = [line for line in f.read().splitlines() if line.strip() and not line.strip().startswith('#')]

    base_dir_line = ""
    for line in lines:
        if line.startswith("BASE_DIR"):
            base_dir_line = line
            break

    if exe_or_tests == "exe":
        ok = "sys.argv[0]" in base_dir_line
        if not ok:
            print("error: check BASE_DIR in config.py; it's not set for EXE creation", file=sys.stderr)
            return False

    if exe_or_tests == "tests":
        ok = "__file__" in base_dir_line
        if not ok:
            print("error: check BASE_DIR in config.py; it's not set for tests", file=sys.stderr)
            return False

    return True


def replace_line_in_file(fname, before, after):
    print(f"┌ start: replace line in {fname}")
    bak = fname + ".bak"
    with open(fname, 'r') as f:
        with open(bak, 'w') as to:
            for line in f:
                line = line.rstrip("\n")
                if line == before:
                    line = after
                to.write(line + "\n")
            #
        #
    #
    old = Path(fname)
    new = Path(bak)
    if new.is_file() and os.path.getsize(str(new)) > 0:
        new.rename(old)
    else:
        print("Error: replace line didn't succeed")
    print(f"└ end: replace line in {fname}")


###########
## Tasks ##
###########

@task()
def clean():
    """
    remove (1) PyInstaller files and directories and (2) the log file
    """
    remove_file("start.spec")
    remove_file("info.log")
    remove_directory("build")
    remove_directory("dist")
    remove_file("monkeytype.sqlite3")


@task()
def _clean_dist():
    """
    delete the folders `dist/assets` and `dist/categories`
    """
    remove_directory("dist/assets")
    remove_directory("dist/categories")


@task(_clean_dist)
def exe():
    """
    create executable with PyInstaller
    """
    if verify_config_file("exe"):
        call_external_command("pyinstaller --onefile --icon=assets/icon.ico start.py")
        copy_dir("assets", "dist/assets")
        remove_directory("dist/assets/screenshots")
        copy_file("categories/categories.yaml", "dist/categories")
        copy_file("bookmarks/bookmarks.yaml", "dist/bookmarks")
        copy_file("tools/verify_your_api_keys.py", "dist/tools")
        copy_file("preferences.ini", "dist/")
        if platform == "linux":
            rename_file("dist/start", "dist/jive")
        elif platform == "windows":
            rename_file("dist/start.exe", "dist/jive.exe")


@task()
def tests():
    """
    run tests
    """
    if verify_config_file("tests"):
        remove_directory("tests/__pycache__")
        my_env = os.environ.copy()
        my_env["PYTHONPATH"] = "."
        cmd = "pytest -vs tests/"
        call_popen_with_env(cmd, env=my_env)


@task()
def mypy():
    """
    run mypy
    """
    cmd = "mypy --config-file mypy.ini jive/"
    call_external_command(cmd)


@task()
def ui_compile():
    """
    compile .ui files
    """
    compile_ui_file(in_file="jive/tabs.ui", out_file="jive/showTabs.py")
    compile_ui_file(in_file="jive/urllist.ui", out_file="jive/showUrlList.py")
    compile_ui_file(in_file="jive/folding.ui", out_file="jive/showFolding.py")
    #
    replace_line_in_file(fname="jive/showTabs.py",
                         before="import icons_rc",
                         after="from jive import icons_rc")
    replace_line_in_file(fname="jive/showUrlList.py",
                         before="import icons_rc",
                         after="from jive import icons_rc")
    replace_line_in_file(fname="jive/showFolding.py",
                        before="import icons_rc",
                        after="from jive import icons_rc")


@task()
def rc_compile():
    """
    compile .qrc resource file
    """
    compile_rc_file(in_file="jive/icons.qrc", out_file="jive/icons_rc.py")


@task(rc_compile, ui_compile)
def all_compile():
    """
    compile everything (.ui files and .qrc)
    """
    pass
