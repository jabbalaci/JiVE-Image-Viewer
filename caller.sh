#!/usr/bin/env bash

SCRIPT=`realpath -s $0`
SCRIPTPATH=`dirname $SCRIPT`

bak=$PWD

cd $SCRIPTPATH
VENV_DIR=`pipenv --venv`
cd $bak

export PATH=$VENV_DIR/bin:$PATH

$SCRIPTPATH/start.py "$@"

# VENV_DIR=`cat $SCRIPTPATH/cd_venv_dir.sh | sed -e 's/^cd //' -e 's/"//g'`
# VENV_DIR=`pipenv --venv`
#
# export PATH=$VENV_DIR/bin:$PATH
#
# $SCRIPTPATH/start.py "$@"

# cd $SCRIPTPATH
# pipenv run python start.py "$@"
