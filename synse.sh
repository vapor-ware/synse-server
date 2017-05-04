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

version="$(python synse/version.py)"


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

  By default, the Synse service will run. Additional flags
  can be provided to the docker run command to modify the behavior,
  e.g. 'docker run vaporio/synse-server [optional arguments]'

  Optional Flags:
    --help | -h         Show this message
    --emulate-plc       Start the PLC emulator
    --emulate-i2c       Start the I2C emulator
    --emulate-rs485     Start the RS485 emulator

  Optional Parameters:
    --emulate-plc-with-cfg [file]
            Start the PLC emulator, using the specified file
            as the emulator's backing data file.

    --emulate-i2c-with-cfg [file]
            Start the I2C emulator, using the specified file
            as the emulator's backing data file.

    --emulate-rs485-with-cfg [file]
            Start the RS485 emulator, using the specified file
            as the emulator's backing data file.
USAGE
}; function --help { -h ;}


# emulate PLC
#   start the PLC emulator with either a specified
#   configuration, or a default configuration file.
function --emulate-plc-with-cfg {
    socat PTY,link=/dev/ttyVapor001,mode=666 PTY,link=/dev/ttyVapor002,mode=666 &
    python -u ./synse/emulator/plc/devicebus_emulator.py $1 &

}; function --emulate-plc { --emulate-plc-with-cfg ./synse/emulator/plc/data/example.json ;}


# emulate I2C
#   start the I2C emulator with either a specified
#   configuration, or a default configuration file.
function --emulate-i2c-with-cfg {
    cp ./configs/synse_config_i2c_emulator.json ./default/default.json

    # test flag to let us bypass the default prop-in of i2c config for bind-mount from test yml
    if [ ! ${VAPOR_TEST} ]; then
        cp ./configs/i2c_emulator_config.json ./i2c_config.json
    fi

    socat PTY,link=/dev/ttyVapor005,mode=666 PTY,link=/dev/ttyVapor006,mode=666 &
    python -u ./synse/emulator/i2c/i2c_emulator.py $1 &

}; function --emulate-i2c { --emulate-i2c-with-cfg ./synse/emulator/i2c/data/example.json ;}


# emulate RS485
#   start the RS485 emulator with either a specified
#   configuration, or a default configuration file.
function --emulate-rs485-with-cfg {
    cp ./configs/synse_config_rs485_emulator.json ./default/default.json

    # test flag to let us bypass the default prop-in of rs485 config for bind-mount from test yml
    if [ ! ${VAPOR_TEST} ]; then
        cp ./configs/rs485_emulator_config.json ./rs485_config.json
    fi

    socat PTY,link=/dev/ttyVapor003,mode=666 PTY,link=/dev/ttyVapor004,mode=666 &
    python -u ./synse/emulator/rs485/rs485_emulator.py $1 &

}; function --emulate-rs485 { --emulate-rs485-with-cfg ./synse/emulator/rs485/data/example.json ;}


_setup_container_environment() {
    if [[ ${VAPOR_DEBUG} && ${VAPOR_DEBUG} = "true" ]]
    then
        mv -f /synse/configs/logging_synse_debug.json /synse/logging_synse.json
        mv -f /synse/configs/logging_emulator_debug.json /synse/logging_emulator.json
    fi

    chown root:www-data /logs
    chmod 775 /logs
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
service nginx restart 2>&1
uwsgi --emperor /etc/uwsgi/emperor.ini 2>&1
