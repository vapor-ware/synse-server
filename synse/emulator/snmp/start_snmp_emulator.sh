#!/bin/bash
# ---------------------------------------------------------------------
# Copyright (C) 2015-17  Vapor IO
#
# This file is part of Synse.
#
# Synse is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Synse is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Synse.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------------------------------------------

# Start the snmp emulator.

# Args are:
# data directory
# port
# log file name

# Adding a json configuration file here gets really tricky.
# The snmp emulator cannot run as root.
# Running a python file to load a configuration file will work,
# but then we don't have access to things like snmpsimd.py when we Popen.
# It is not a path issue.
#
# Put the writecache file in /home/snmp rather than /tmp since the user snmp will have access
#

python `which snmpsimd.py` \
    --data-dir=$1 \
    --agent-udpv4-endpoint=0.0.0.0:$2 \
    --variation-module-options=writecache:file:/home/snmp/snmp-emulator-writecache.db \
    2>&1 | tee /logs/$3
