#!/usr/bin/python
"""
   OpenDCRE Device Bus Test Emulator
   Author:  andrew
   Date:    4/16/2015
   Updated: 6/11/2015 - Add power control/status commands (andrew)

        \\//
         \/apor IO

    Copyright (C) 2015  Vapor IO

    This file is part of OpenDCRE.

    OpenDCRE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    OpenDCRE is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with OpenDCRE.  If not, see <http://www.gnu.org/licenses/>.

"""
import sys
import logging
import json

import devicebus

DEBUG = False                   # set to true for more console logging
logger = logging.getLogger()
TERMINATE = False               # set to true to shut down the emulator
configuration = {}              # where our configuration will live

"""
    This emulator is designed to stand-in for the actual OpenDCRE device Bus
    Pi Hat hardware, which is addressable via serial communications.

    The emulator takes as its first parameter the name of the TTY (PTY) device
    that will communicate with an upper level client (e.g. the Southbound API
    endpoint).  Given this device name, the emulator opens a serial connection,
    and starts by listening for a request, and responding with a response.

    The second parameter the emulator takes is a file name for a JSON file that
    contains emulator configuration directives.

    IMPORTANT:  In order to make the emulator work, one additional component is
                required:  socat (http://www.dest-unreach.org/socat)

                socat is used to create and link two virtual serial ports.
                e.g.:
                    sudo socat PTY,link=/dev/ttyVapor001,mode=666,user=acencini
                        PTY,link=/dev/ttyVapor002,mode=666,user=acencini

                socat will be added to Vapor docker images, and is easily
                installable (apt-get install socat) on most Linux systems.

                ON MACOS, socat requires a modest amount more work:

                wget http://www.dest-unreach.org/socat/download/socat-2.0.0-b8.tar.gz
                tar xzvf socat-2.0.0-b8.tar.gz
                cd socat-2.0.0-b8.tar.gz
                ./configure
                make
                sudo make install

    Enjoy.
"""

def main(emulatorDevice):
    emulator = devicebus.initialize(emulatorDevice, timeout=None)
    read_i = 0

    while not TERMINATE:
        # retrieve packet from client
        packet = devicebus.DeviceBusPacket(serial_reader=emulator)
        logger.debug(" * EMULATOR<<: " + str([hex(x) for x in packet.serialize()]))
        # inspect packet and pass to appropriate handler
        #   NB in the future could make arbitrary function a handler
        cmd = chr(packet.data[0])
        if cmd == 'D':
            # ======================> SCAN <======================
            sc = devicebus.DumpCommand(bytes=packet.serialize())
            # match sc.board_id against a board_id in configuration - if
            # the board_id does not exist, send nothing; if board_id is 0xFF
            # return all boards unless we are emulating early firmware not
            # supporting scan-all-boards, where we instead return nothing
            if sc.board_id != 0xFF:         # TODO: support scan all (not in fw yet)
                for board in configuration["boards"]:
                    if board["board_id"] == sc.board_id:
                        if "raw_data" in board:
                            emulator.write(board["raw_data"])
                            emulator.flush()
                        else:
                            for port in board["ports"]:
                                srp = devicebus.DumpResponse(
                                    board_id=board["board_id"],
                                    port_id=port["port_index"],
                                    device_id=port["device_id"],
                                    device_type=devicebus.get_device_type_code(port["device_type"]),
                                    data=[devicebus.get_device_type_code(port["device_type"])]
                                )
                                # logger.debug(" * EMULATOR<<: " + str([hex(x) for x in srp.serialize()]))
                                emulator.write(srp.serialize())
                                emulator.flush()
                            # we have sent everything from this board
            else:
                # todo - return all boards (scan all) - not supported in FW
                pass
            # if we get here, nothing to send
            pass

        elif cmd == 'V':
            # ======================> VERSION <======================
            # TODO: support a collection of versions in the schema?  maybe.
            vc = devicebus.VersionCommand(bytes=packet.serialize())
            for board in configuration["boards"]:
                if board["board_id"] == vc.board_id:
                    if isinstance(board["firmware_version"], list):
                        # sending raw bytes
                        emulator.write(board["firmware_version"])
                        emulator.flush()
                    else:
                        vr = devicebus.VersionResponse(
                            versionString=board["firmware_version"]
                        )   # TODO: set board_id field?
                        emulator.write(vr.serialize())
                        emulator.flush()
            # otherwise, no response

        elif cmd == 'R':
            # ======================> READ <======================
            rc = devicebus.DeviceReadCommand(bytes=packet.serialize())
            for board in configuration["boards"]:
                if board["board_id"] == rc.board_id:
                    for port in board["ports"]:
                        if (port["port_index"] == rc.port_id) and (port["device_type"] == devicebus.get_device_type_name(rc.device_type)):
                            # now we can craft a response
                            responses_length = len(port["read"]["responses"])
                            # get the responses counter
                            _count = port["read"]["_count"] if "_count" in port["read"] else 0
                            if responses_length > 0 and _count < responses_length:
                                if isinstance(port["read"]["responses"][_count], list):
                                    # we are sending raw bytes
                                    emulator.write(port["read"]["responses"][read_i])
                                    emulator.flush()
                                elif port["read"]["responses"][_count] is not None:
                                    # we are sending back a device reading
                                    reading = [ord(x) for x in str(port["read"]["responses"][_count])]
                                    rr = devicebus.DeviceReadResponse(device_reading=reading)
                                    emulator.write(rr.serialize())
                                    emulator.flush()
                                else:
                                    # otherwise, we do not send a response
                                    pass
                                # now increment index into our responses, and wrap it if
                                # we are repeatable
                                _count += 1
                                if port["read"]["repeatable"]:
                                    _count %= len(port["read"]["responses"])
                                port["read"]["_count"] = _count
                                pass

        elif cmd == 'P':
            # ======================> POWER CONTROL <======================
            # the second character of packet.data is the actual command/action
            pc = devicebus.PowerControlCommand(bytes=packet.serialize())

            # return power status regardless of command - users of the emulator
            # should design the config tests to match the anticipated sequence
            # of commands/requests
            for board in configuration["boards"]:
                if board["board_id"] == pc.board_id:
                    for port in board["ports"]:
                        if (port["port_index"] == pc.port_id) and (port["device_type"] == devicebus.get_device_type_name(pc.device_type)):
                            responses_length = len(port["power"]["responses"])
                            # get the responses counter
                            _count = port["power"]["_count"] if "_count" in port["power"] else 0

                            if responses_length > 0 and _count < responses_length:
                                if isinstance(port["power"]["responses"][_count], list):
                                    # we are sending raw bytes
                                    emulator.write(port["power"]["responses"][_count])
                                    emulator.flush()
                                elif port["power"]["responses"][_count] is not None:
                                    # we are sending back a device reading
                                    powerStatus = [ord(x) for x in str(port["power"]["responses"][_count])]
                                    pr = devicebus.PowerControlResponse(
                                        data=powerStatus)
                                    emulator.write(pr.serialize())
                                    emulator.flush()
                                else:
                                    # otherwise, we do not send a response
                                    pass
                                # now increment index into our responses, and wrap it if
                                # we are repeatable
                                _count += 1
                                if port["power"]["repeatable"]:
                                    _count %= len(port["power"]["responses"])
                                port["power"]["_count"] = _count
                                pass

        # otherwise, no response
        else:
            # ======================> UNKNOWN <======================
            pass


if __name__ == "__main__":
    if DEBUG is True:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(message)s")
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)

    # the serial device we will listen on,
    # passed in as first parameter to this program
    emulatorDevice = sys.argv[1]

    # the JSON configuration file name is
    # passed in as the second parameter to this program
    configFile = sys.argv[2]
    file = open(configFile, "r")
    data = file.read()
    configuration = json.loads(data)

    main(emulatorDevice)
