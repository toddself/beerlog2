#!/bin/sh
CFG=$1

if [ -z $CFG ]
then
    CFG="settings.cfg"
fi

BEERLOG_SETTINGS=$CFG /usr/bin/env python beerlog_tests.py