#!/usr/bin/env bash

SCRIPT=`realpath -s $0`
SCRIPTPATH=`dirname $SCRIPT`

bak="$PWD"

cd $SCRIPTPATH
VENV_DIR=`poetry env info -p`
cd "$bak"

export PATH=$VENV_DIR/bin:$PATH

$SCRIPTPATH/start.py "$@"
