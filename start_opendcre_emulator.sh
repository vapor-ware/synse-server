#!/bin/bash

socat PTY,link=/dev/ttyVapor001,mode=666 PTY,link=/dev/ttyVapor002,mode=666 &
./opendcre_southbound/devicebus_emulator.py /dev/ttyVapor001 ./opendcre_southbound/simple.json &
./start_opendcre.sh /dev/ttyVapor002
