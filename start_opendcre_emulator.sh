#!/bin/bash

if [ $# -eq 0 ]
then
    socat PTY,link=/dev/ttyVapor001,mode=666 PTY,link=/dev/ttyVapor002,mode=666 &
    ./opendcre_southbound/devicebus_emulator.py /dev/ttyVapor001 ./opendcre_southbound/simple.json &
    ./start_opendcre.sh /dev/ttyVapor002
else
    if [ $# -eq 1 ]
    then
        socat PTY,link=/dev/ttyVapor001,mode=666 PTY,link=/dev/ttyVapor002,mode=666 &
        ./opendcre_southbound/devicebus_emulator.py /dev/ttyVapor001 $1 &
        ./start_opendcre.sh /dev/ttyVapor002
    else
        # start emulator with $1 as device, $2 as json config, $3 as hw type
        # from devicebus.py, pass as int:
        #   DEVICEBUS_RPI_HAT_V1 = 0x00
        #   DEVICEBUS_VEC_V1 = 0x10
        #   DEVICEBUS_EMULATOR_V1 = 0x20
        ./opendcre_southbound/devicebus_emulator.py $1 $2 $3
    fi
fi