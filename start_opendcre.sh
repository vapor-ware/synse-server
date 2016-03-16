#!/bin/bash

ARCH=`uname -m`

chown root:www-data /logs
chmod 775 /logs

service nginx start
if [ "$ARCH" = "aarch64" ]
then
	if [ ! -z ${1} ]; then
	    if [ ! -z ${2} ]; then
	        # $1 is the hardware device, $2 is the type of hardware
	        # from devicebus.py (pass as int):
	        #   DEVICEBUS_RPI_HAT_V1 = 0x00
            #   DEVICEBUS_VEC_V1 = 0x10
            #   DEVICEBUS_EMULATOR_V1 = 0x20
    		uwsgi /opendcre/opendcre_uwsgi.ini --plugin python --pyargv "$1 $2" >> /logs/opendcre_daemon.log 2>&1
    	else
    		uwsgi /opendcre/opendcre_uwsgi.ini --plugin python --pyargv $1 >> /logs/opendcre_daemon.log 2>&1
    	fi
	else
		uwsgi /opendcre/opendcre_uwsgi.ini --plugin python >> /logs/opendcre_daemon.log 2>&1
	fi
else
	if [ ! -z ${1} ]; then
	    if [ ! -z ${2} ]; then
	        # $1 is the hardware device, $2 is the type of hardware
	        # from devicebus.py (pass as int):
	        #   DEVICEBUS_RPI_HAT_V1 = 0x00
            #   DEVICEBUS_VEC_V1 = 0x10
            #   DEVICEBUS_EMULATOR_V1 = 0x20
    		uwsgi /opendcre/opendcre_uwsgi.ini --pyargv "$1 $2" >> /logs/opendcre_daemon.log 2>&1
    	else
    		uwsgi /opendcre/opendcre_uwsgi.ini --pyargv $1 >> /logs/opendcre_daemon.log 2>&1
    	fi
	else
		uwsgi /opendcre/opendcre_uwsgi.ini >> /logs/opendcre_daemon.log 2>&1
	fi
fi
