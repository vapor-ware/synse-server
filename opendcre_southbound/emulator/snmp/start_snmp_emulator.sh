#!/bin/bash

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
