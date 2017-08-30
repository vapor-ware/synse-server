#!/usr/bin/env bash
#
#    \\//
#     \/apor IO
#
# Start the sensor readers that own the buses.
#
python synse/sensors/i2c/i2c_daemon.py &
python synse/sensors/rs485/rs485_daemon.py &
