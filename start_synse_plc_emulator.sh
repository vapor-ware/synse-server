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

# first, determine if we are in debug mode, in which case we prop debug log config over prod log config
if [[ $VAPOR_DEBUG && ${VAPOR_DEBUG} = "true" ]]
then
    mv -f /synse/configs/logging_synse_debug.json /synse/logging_synse.json
    mv -f /synse/configs/logging_emulator_debug.json /synse/logging_emulator.json
fi

socat PTY,link=/dev/ttyVapor001,mode=666 PTY,link=/dev/ttyVapor002,mode=666 &

# First parameter is the json configuration file, else use the default file.
if [ $# -eq 1 ]
    then
        python -u ./synse/emulator/plc/devicebus_emulator.py $1 &
    else
        python -u ./synse/emulator/plc/devicebus_emulator.py ./synse/emulator/plc/data/example.json &
fi
./start_synse.sh /dev/ttyVapor002
