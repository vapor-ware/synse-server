#!/bin/bash
# ---------------------------------------------------------------------
# Copyright (C) 2015-17  Vapor IO
#
# This file is part of OpenDCRE.
#
# OpenDCRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# OpenDCRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OpenDCRE.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------------------------------------------

# first, determine if we are in debug mode, in which case we prop debug log config over prod log config
if [[ $VAPOR_DEBUG && ${VAPOR_DEBUG} = "true" ]]
then
    mv -f /opendcre/configs/logging_bootstrap_debug.json /opendcre/logging_bootstrap.json
    mv -f /opendcre/configs/logging_opendcre_debug.json /opendcre/logging_opendcre.json
    mv -f /opendcre/configs/logging_emulator_debug.json /opendcre/logging_emulator.json
fi


ARCH=`uname -m`

chown root:www-data /logs
chmod 775 /logs

service nginx restart 2>&1

#
#if [ "$ARCH" = "aarch64" ]
#then
#	if [ ! -z ${1} ]; then
#	    if [ ! -z ${2} ]; then
#	        # $1 is the hardware device, $2 is the type of hardware
#	        # from devicebus.py (pass as int):
#	        #   DEVICEBUS_RPI_HAT_V1 = 0x00
#            #   DEVICEBUS_VEC_V1 = 0x10
#            #   DEVICEBUS_EMULATOR_V1 = 0x20
#    		uwsgi --emperor /etc/uwsgi/emperor.ini --plugin python --pyargv "$1 $2" 2>&1
#    	else
#    		uwsgi --emperor /etc/uwsgi/emperor.ini --plugin python --pyargv $1 2>&1
#    	fi
#	else
#		uwsgi --emperor /etc/uwsgi/emperor.ini --plugin python 2>&1
#	fi
#else
#	if [ ! -z ${1} ]; then
#	    if [ ! -z ${2} ]; then
#	        # $1 is the hardware device, $2 is the type of hardware
#	        # from devicebus.py (pass as int):
#	        #   DEVICEBUS_RPI_HAT_V1 = 0x00
#            #   DEVICEBUS_VEC_V1 = 0x10
#            #   DEVICEBUS_EMULATOR_V1 = 0x20
#    		uwsgi --emperor /etc/uwsgi/emperor.ini --pyargv "$1 $2" 2>&1
#    	else
#    		uwsgi --emperor /etc/uwsgi/emperor.ini --pyargv $1 2>&1
#    	fi
#	else
#		uwsgi --emperor /etc/uwsgi/emperor.ini 2>&1
#	fi
#fi


uwsgi --emperor /etc/uwsgi/emperor.ini 2>&1