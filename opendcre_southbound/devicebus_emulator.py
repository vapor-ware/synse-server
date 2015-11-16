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
from definitions import SCAN_ALL_BIT, SAVE_BIT

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


# ================================================================================= #
#                         Emulator Convenience Methods                              #
# ================================================================================= #

def board_ids_match(config_board, dev_bus_cmd):
    """ Check that the configuration board id matches the command's board id.

    Convenience method to check that the configuration's board id matches the
    board id from the devicebus command. this requires a type conversion, since
    the config's board id is a hex-string and the devicebus command's board id
    is a hexadecimal value.
    """
    return int(config_board['board_id'], 16) == dev_bus_cmd.board_id


def device_ids_match(config_port, dev_bus_cmd):
    """ Check that the configuration device id matches the command's device id.

    Convenience method to check that the configuration's device id matches the
    device id from the devicebus command. this requires a type conversion, since
    the config's device id is a hex-string and the devicebus command's device id
    is a hexadecimal value.
    """
    return int(config_port['device_id'], 16) == dev_bus_cmd.device_id


# ================================================================================= #
#                                 Emulator Main                                     #
# ================================================================================= #


def main(emulatorDevice):
    emulator = devicebus.initialize(emulatorDevice, timeout=None)

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
            # if the save bit is enabled in the board_id, do nothing, since we
            # expect no response back in this case.
            if (sc.board_id >> SAVE_BIT) == 1:
                pass
            # match sc.board_id against a board_id in configuration - if
            # the board_id does not exist, send nothing; if board_id is 0xFF
            # return all boards unless we are emulating early firmware not
            # supporting scan-all-boards, where we instead return nothing
            if (sc.board_id >> SCAN_ALL_BIT) != 1:
                for board in configuration["boards"]:
                    if board_ids_match(board, sc):
                        if "raw_data" in board:
                            emulator.write(board["raw_data"])
                            emulator.flush()
                        else:
                            for device in board["devices"]:
                                srp = devicebus.DumpResponse(
                                    board_id=board["board_id"],
                                    device_id=device["device_id"],
                                    device_type=devicebus.get_device_type_code(device["device_type"]),
                                    data=[devicebus.get_device_type_code(device["device_type"])]
                                )
                                # logger.debug(" * EMULATOR<<: " + str([hex(x) for x in srp.serialize()]))
                                emulator.write(srp.serialize())
                                emulator.flush()
                            # we have sent everything from this board
            else:
                for board in configuration["boards"]:
                    if "raw_data" in board:
                        emulator.write(board["raw_data"])
                        emulator.flush()
                    else:
                        for device in board["devices"]:
                            srp = devicebus.DumpResponse(
                                board_id=board["board_id"],
                                device_id=device["device_id"],
                                device_type=devicebus.get_device_type_code(device["device_type"]),
                                data=[devicebus.get_device_type_code(device["device_type"])]
                            )
                            emulator.write(srp.serialize())
                            emulator.flush()
            # if we get here, nothing to send
            pass

        elif cmd == 'V':
            # ======================> VERSION <======================
            # TODO: support a collection of versions in the schema?  maybe.
            vc = devicebus.VersionCommand(bytes=packet.serialize())
            for board in configuration["boards"]:
                if board_ids_match(board, vc):
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
            # first, determine what kind of a read we are dealing with
            if len(packet.data) == 1:
                # data -> ["R"] : Read Command
                rc = devicebus.DeviceReadCommand(bytes=packet.serialize())
                for board in configuration["boards"]:
                    if board_ids_match(board, rc):
                        for device in board["devices"]:
                            if device_ids_match(device, rc) and (device["device_type"] == devicebus.get_device_type_name(rc.device_type)):
                                # now we can craft a response
                                responses_length = len(device["read"]["responses"])
                                # get the responses counter
                                _count = device["read"]["_count"] if "_count" in device["read"] else 0
                                if responses_length > 0 and _count < responses_length:
                                    if isinstance(device["read"]["responses"][_count], list):
                                        # we are sending raw bytes
                                        emulator.write(device["read"]["responses"][_count])
                                        emulator.flush()
                                    elif device["read"]["responses"][_count] is not None:
                                        # we are sending back a device reading
                                        reading = [ord(x) for x in str(device["read"]["responses"][_count])]
                                        rr = devicebus.DeviceReadResponse(device_reading=reading)
                                        emulator.write(rr.serialize())
                                        emulator.flush()
                                    else:
                                        # otherwise, we do not send a response
                                        pass
                                    # now increment index into our responses, and wrap it if
                                    # we are repeatable
                                    _count += 1
                                    if device["read"]["repeatable"]:
                                        _count %= len(device["read"]["responses"])
                                    device["read"]["_count"] = _count
                                    pass

            else:
                read_type = chr(packet.data[1])
                if read_type == 'I':
                    # data -> ["R", "I"] : Read Asset Info
                    rai = devicebus.ReadAssetInfoCommand(bytes=packet.serialize())
                    for board in configuration["boards"]:
                        if board_ids_match(board, rai):
                            for device in board["devices"]:
                                if device_ids_match(device, rai) and (device["device_type"] == devicebus.get_device_type_name(rai.device_type)):
                                    # now we can craft a response
                                    rair = devicebus.ReadAssetInfoResponse(
                                        board_id=board["board_id"],
                                        device_id=device["device_id"],
                                        device_type=devicebus.get_device_type_code(device["device_type"]),
                                        asset_info=device["asset_info"]
                                    )
                                    emulator.write(rair.serialize())
                                    emulator.flush()
                    # otherwise, no response

        elif cmd == 'P':
            # ======================> POWER CONTROL <======================
            # the second character of packet.data is the actual command/action
            pc = devicebus.PowerControlCommand(bytes=packet.serialize())

            # return power status regardless of command - users of the emulator
            # should design the config tests to match the anticipated sequence
            # of commands/requests
            for board in configuration["boards"]:
                if board_ids_match(board, pc):
                    for device in board["devices"]:
                        if device_ids_match(device, pc) and (device["device_type"] == devicebus.get_device_type_name(pc.device_type)):
                            responses_length = len(device["power"]["responses"])
                            # get the responses counter
                            _count = device["power"]["_count"] if "_count" in device["power"] else 0

                            if responses_length > 0 and _count < responses_length:
                                if isinstance(device["power"]["responses"][_count], list):
                                    # we are sending raw bytes
                                    emulator.write(device["power"]["responses"][_count])
                                    emulator.flush()
                                elif device["power"]["responses"][_count] is not None:
                                    # we are sending back a device reading
                                    powerStatus = [ord(x) for x in str(device["power"]["responses"][_count])]
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
                                if device["power"]["repeatable"]:
                                    _count %= len(device["power"]["responses"])
                                device["power"]["_count"] = _count
                                pass
                    # otherwise, no response

        elif cmd == 'W':
            # ======================> WRITE <======================
            # first, determine what kind of a read we are dealing with
            if len(packet.data) == 1:
                # unsupported read
                pass

            else:
                # write asset info
                write_type = chr(packet.data[1])
                if write_type == 'I':
                    wai = devicebus.WriteAssetInfoCommand(bytes=packet.serialize())
                    for board in configuration["boards"]:
                        if board_ids_match(board, wai):
                            for device in board["devices"]:
                                if device_ids_match(device, wai) and (device["device_type"] == devicebus.get_device_type_name(wai.device_type)):
                                    # update the asset info field - here we slice wai.data from the 2nd
                                    # index until the end, because the first two byte contain the "W" "I"
                                    # commands which tell us this is an asset write. the remaining bytes
                                    # are the payload for what gets updated.
                                    device["asset_info"] = ''.join([chr(x) for x in wai.data[2:]])
                                    # now we can craft a response
                                    wair = devicebus.WriteAssetInfoResponse(
                                        board_id=board["board_id"],
                                        device_id=device["device_id"],
                                        device_type=devicebus.get_device_type_code(device["device_type"]),
                                        asset_info=device["asset_info"]
                                    )
                                    emulator.write(wair.serialize())
                                    emulator.flush()
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
