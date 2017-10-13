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
set -o errexit -o pipefail

version="$(python /synse/synse/version.py)"


# help
#   display usage information
function -h {
cat <<USAGE
   __
  / _\_   _ _ __  ___  ___
  \ \| | | | '_ \/ __|/ _ \\
  _\ \ |_| | | | \__ \  __/
  \__/\__, |_| |_|___/\___| v${version}
      |___/

    Vapor IO

  Synse provides an API for monitoring and control of data center
  and IT equipment, including reading sensors and server power
  control - via. IPMI, PLC, RS485, I2C, SNMP, and Redfish.

  By default, the Synse service will run. Additional subcommands
  can be specified to start up various emulators alongside Synse.
  IPMI, SNMP, and Redfish emulators all run external to the
  Synse container, but PLC, RS485, and I2C can be started parallel
  to Synse.

  USAGE:  docker run vaporio/synse-server [flag | subcommand]

  Flags:
    --help | -h     Show this message.
    --version | -v  Show the version of Synse.

  Subcommands:
    start-plc-emulator [file]
            Start the PLC emulator without any Synse configurations
            put into place. With this, it is up to the user to make
            sure Synse has a PLC device (or devices) correctly
            configured (in the default/override config for devices).

            This can take a filename as a parameter to specify an
            emulator configuration.

    start-i2c-emulator [file]
            Start the I2C emulator without any Synse configurations
            put into place. With this, it is up to the user to make
            sure Synse has an I2C device (or devices) correctly
            configured (in the default/override config for devices).

            This can take a filename as a parameter to specify an
            emulator configuration.

    start-rs485-emulator [file]
            Start the RS485 emulator without any Synse configurations
            put into place. With this, it is up to the user to make
            sure Synse has an RS485 device (or devices) correctly
            configured (in the default/override config for devices).

            This can take a filename as a parameter to specify an
            emulator configuration.

    start-sensor-readers
            Start the sensor readers that own the buses.

    emulate-plc
            Start the PLC emulator. A default configuration file
            will be used.

    emulate-i2c
            Start the I2C emulator. A default configuration file
            will be used.

    emulate-rs485
            Start the RS485 emulator. A default configuration file
            will be used.

    emulate-plc-with-cfg [file]
            Start the PLC emulator, using the specified file as the
            emulator's backing data file.

    emulate-i2c-with-cfg [file]
            Start the I2C emulator, using the specified file as the
            emulator's backing data file.

    emulate-rs485-with-cfg [file]
            Start the RS485 emulator, using the specified file as the
            emulator's backing data file.

USAGE
exit 0
}; function --help { -h ;}


# version
#   show the version of synse
function -v {
    echo "${version}"
}; function --version { -v ;}


# emulate PLC
#   start the PLC emulator with either a specified
#   configuration, or a default configuration file.
function start-plc-emulator {
    socat PTY,link=/dev/ttyVapor001,mode=666 PTY,link=/dev/ttyVapor002,mode=666 &
    python -u /synse/synse/emulator/plc/devicebus_emulator.py $1 &

    # Sleep for a short bit - this is to give the emulator enough time to start
    # up and configure before synse starts hitting it with requests.
    sleep 0.25

}; function emulate-plc-with-cfg {
    start-plc-emulator $1

}; function emulate-plc { emulate-plc-with-cfg /synse/synse/emulator/plc/data/example.json ;}


# emulate I2C
#   start the I2C emulator with either a specified
#   configuration, or a default configuration file.
function start-i2c-emulator {
    socat PTY,link=/dev/ttyVapor005,mode=666 PTY,link=/dev/ttyVapor006,mode=666 &
    python -u /synse/synse/emulator/i2c/i2c_emulator.py $1 &

    # Sleep for a short bit - this is to give the emulator enough time to start
    # up and configure before synse starts hitting it with requests.
    sleep 0.25

}; function emulate-i2c-with-cfg {
    cp /synse/configs/synse/i2c/synse_config.json /synse/override/i2c_config.json

    # test flag to let us bypass the default prop-in of i2c config for bind-mount from test yml
    if [ ! ${VAPOR_TEST} ]; then
        cp /synse/configs/synse/i2c/i2c_config.json /synse/i2c_config.json
    fi

    start-i2c-emulator $1

}; function emulate-i2c { emulate-i2c-with-cfg /synse/synse/emulator/i2c/data/example.json ;}


# emulate RS485
#   start the RS485 emulator with either a specified
#   configuration, or a default configuration file.
function start-rs485-emulator {
    socat PTY,link=/dev/ttyVapor003,mode=666 PTY,link=/dev/ttyVapor004,mode=666 &
    python -u /synse/synse/emulator/rs485/rs485_emulator.py $1 &

    # Sleep for a short bit - this is to give the emulator enough time to start
    # up and configure before synse starts hitting it with requests.
    sleep 0.25

}; function emulate-rs485-with-cfg {
    cp /synse/configs/synse/rs485/synse_config.json /synse/override/rs485_config.json

    # test flag to let us bypass the default prop-in of rs485 config for bind-mount from test yml
    if [ ! ${VAPOR_TEST} ]; then
        cp /synse/configs/synse/rs485/rs485_config.json /synse/rs485_config.json
    fi

    start-rs485-emulator $1;

}; function emulate-rs485 { emulate-rs485-with-cfg /synse/synse/emulator/rs485/data/example.json ;}

# Start the sensor readers that own the buses.
function start-sensor-readers {
    synse/sensors/start_sensor_readers.sh &
}

_setup_container_environment() {
    if [[ ${VAPOR_DEBUG} && ${VAPOR_DEBUG} = "true" ]]
    then
        mv -f /synse/configs/logging/synse_debug.json /synse/configs/logging/synse.json
        mv -f /synse/configs/logging/emulator_debug.json /synse/configs/logging/emulator.json
    fi
}


function msg { out "$*" >&2 ;}
function err { local x=$? ; msg "$*" ; return $(( $x == 0 ? 1 : $x )) ;}
function out { printf '%s\n' "$*" ;}


# if any arguments were passed in, act on them now. arguments
# will either prompt the usage to be displayed or will start
# a single emulator.
#
# note that only a single emulator can be started with a single
# synse instance.
if [[ ${1:-} ]] && declare -F | cut -d' ' -f3 | fgrep -qx -- "${1:-}"
then "$@"
fi

# start synse
_setup_container_environment
start-sensor-readers # TODO: Does not belong in open source synse, nor do the daemons.
service nginx restart 2>&1
uwsgi --ini /etc/uwsgi/synse.ini 2>&1
