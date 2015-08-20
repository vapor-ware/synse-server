#!/bin/bash

service nginx start
if [ ! -z ${1} ]; then
	uwsgi /opendcre/opendcre_uwsgi.ini --pyargv $1 >> /logs/opendcre_daemon.log 2>&1
else
	uwsgi /opendcre/opendcre_uwsgi.ini >> /logs/opendcre_daemon.log 2>&1
fi
