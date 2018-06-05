#!/usr/bin/env bash

SCRIPT=`realpath -s $0`
SCRIPTPATH=`dirname $SCRIPT`
cd $SCRIPTPATH

VENV_DIR=`cat cd_venv_dir.sh | sed -e 's/^cd //' -e 's/"//g'`

export PATH=$VENV_DIR/bin:$PATH

./start.py "$@"
