#!/bin/bash

service nginx start
if [ ! -z ${1} ]; then
	uwsgi /opendcre/opendcre_uwsgi.ini --pyargv $1
else
	uwsgi /opendcre/opendcre_uwsgi.ini
fi
