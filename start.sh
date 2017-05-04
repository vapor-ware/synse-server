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

version="$(python synse/version.py)"


setup_container_environment() {
    if [[ ${VAPOR_DEBUG} && ${VAPOR_DEBUG} = "true" ]]
    then
        mv -f /synse/configs/logging_synse_debug.json /synse/logging_synse.json
        mv -f /synse/configs/logging_emulator_debug.json /synse/logging_emulator.json
    fi

    chown root:www-data /logs
    chmod 775 /logs
}


show_help() {
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
}


start_plc_emulator() {
    socat PTY,link=/dev/ttyVapor001,mode=666 PTY,link=/dev/ttyVapor002,mode=666 &

    if [ $# -eq 1 ]; then
        python -u ./synse/emulator/plc/devicebus_emulator.py $1 &
    else
        python -u ./synse/emulator/plc/devicebus_emulator.py ./synse/emulator/plc/data/example.json &
    fi
}


start_i2c_emulator() {
    cp ./configs/synse_config_i2c_emulator.json ./default/default.json

    # test flag to let us bypass the default prop-in of i2c config for bind-mount from test yml
    if [ ! ${VAPOR_TEST} ]; then
        cp ./configs/i2c_emulator_config.json ./i2c_config.json
    fi

    socat PTY,link=/dev/ttyVapor005,mode=666 PTY,link=/dev/ttyVapor006,mode=666 &

    if [ $# -eq 1 ]; then
        python -u ./synse/emulator/i2c/i2c_emulator.py $1 &
    else
        python -u ./synse/emulator/i2c/i2c_emulator.py ./synse/emulator/i2c/data/example.json &
    fi
}


start_rs485_emulator() {
    cp ./configs/synse_config_rs485_emulator.json ./default/default.json

    # test flag to let us bypass the default prop-in of rs485 config for bind-mount from test yml
    if [ ! ${VAPOR_TEST} ]; then
        cp ./configs/rs485_emulator_config.json ./rs485_config.json
    fi

    socat PTY,link=/dev/ttyVapor003,mode=666 PTY,link=/dev/ttyVapor004,mode=666 &

    if [ $# -eq 1 ]; then
        python -u ./synse/emulator/rs485/rs485_emulator.py $1 &
    else
        python -u ./synse/emulator/rs485/rs485_emulator.py ./synse/emulator/rs485/data/example.json &
    fi
}


# -----------------------------
# Synse Startup
# -----------------------------

# first, setup the container environment - this sets permissions where needed
# and checks to see if we should be using a debug logger.
setup_container_environment

# make sure nginx is running
service nginx restart 2>&1

# parse any arguments passed to synse. arguments passed to synse are used to
# enable and configure emulators to run alongside Synse for development, testing,
# or just getting a feel for synse in a safe environment.
while [[ "$#" > 0 ]]; do
    case $1 in
        --emulate-plc)
            start_plc_emulator
            ;;
        --emulate-plc-with-cfg)
            shift;
            start_plc_emulator $1
            ;;
        --emulate-i2c)
            start_i2c_emulator
            ;;
        --emulate-i2c-with-cfg)
            shift;
            start_i2c_emulator $1
            ;;
        --emulate-rs485)
            start_rs485_emulator
            ;;
        --emulate-rs485-with-cfg)
            shift;
            start_rs485_emulator $1
            ;;
        --help|-h)
            show_help
            ;;
        *)
            break
            ;;
    esac
    shift;
done

# finally, start synse
uwsgi --emperor /etc/uwsgi/emperor.ini 2>&1
