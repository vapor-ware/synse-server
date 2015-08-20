#!/usr/bin/python
'''
   OpenDCRE Southbound API Endpoint
   Author:  andrew
   Date:    4/8/2015
   Update:  6/11/2015 - Support power control commands/responses. Minor bug
                        fixes and sensor/device renaming. (ABC)
            6/19/2015 - Add locking to prevent multiple simultaneous requests
                        from stomping all over the bus.
            7/20/2015 - add node information
            7/28/2015 - convert to python package

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

'''

PREFIX = "/opendcre/"               # URL prefix for REST access
SERIAL_DEFAULT = "/dev/ttyAMA0"      # default serial device to use for bus
DEBUG = False                        # set to False to disable extra logging
LOCKFILE = "/tmp/OpenDCRE.lock"     # to prevent chaos on the serial bus

from version import __version__      # full opendcre version
from version import __api_version__  # major.minor API version

from flask import Flask
from flask import jsonify
from flask import abort

# for sync on the serial bus
from lockfile import LockFile

import devicebus
import serial
import sys
import time
import logging

app = Flask(__name__)
logger = logging.getLogger()

@app.route(PREFIX+__api_version__+"/test", methods=['GET', 'POST'])
def test_routine():
    """ Test routine to verify the endpoint is running and ok, without
        relying on the serial bus layer.
    """
    return jsonify({"status":"ok"})

@app.route(PREFIX+__api_version__+"/version/<int:boardNum>", methods=['GET'])
def get_board_version(boardNum):
    """ Get board version given the specified board number.

    Args:  boardNum is the board number to get version for.

    Returns:  The version of the hardware and firmware for the given board.

    Raises:   Returns a 500 error if the scan command fails.

    """

    # TODO: this is a very aggressive locking strategy.  we could release
    #       the lockfile once we've gotten our response back, prior to
    #       returning results.  this could be tidied up.
    with LockFile(LOCKFILE):
        bus = devicebus.initialize(app.config["SERIAL"])
        vc = devicebus.VersionCommand(board_id=boardNum, sequence=0x01)
        bus.write(vc.serialize())

        logger.debug(" * FLASK>>: " + str([hex(x) for x in vc.serialize()]))

        try:
            vr = devicebus.VersionResponse(serial_reader=bus)
        except devicebus.BusTimeoutException:
            abort(500)

        logger.debug(" * FLASK<<: " + str([hex(x) for x in vr.serialize()]))

        return jsonify({"firmware_version":vr.versionString,
            "opendcre_version":__version__,
            "api_version":__api_version__})


@app.route(PREFIX+__api_version__+"/scan/<int:boardNum>", methods=['GET'])
def get_board_ports(boardNum):
    """ Query a specific board, given the board id, and provide the
        active devices on that board.

    Args:  boardNum is the board number to dump.  If 0xFF then scan
            all boards on the bus.

    Returns:  Active device ports, numbers and types from the given board(s).

    Raises:   Returns a 500 error if the scan command fails.

    """
    with LockFile(LOCKFILE):
        bus = devicebus.initialize(app.config["SERIAL"])
        response_dict = {"boards" : []}
        dc = devicebus.DumpCommand(board_id=boardNum, sequence=0x01)
        bus.write(dc.serialize())

        logger.debug(" * FLASK>>: " + str([hex(x) for x in dc.serialize()]))

        try:
            dr = devicebus.DumpResponse(serial_reader=bus)
        except devicebus.BusTimeoutException:
            # in this case, we cannot move further
            abort(500)

        # add the initial board/port record to the response
        response_dict["boards"].append(
            {
                "board_id": dr.board_id,
                "ports": [{
                    "port_index": dr.port_id,
                    "device_id": dr.device_id,
                    "device_type": devicebus.get_device_type_name(dr.data[0])
                }]
            }
        )

        logger.debug(" * FLASK<<: " + str([hex(x) for x in dr.serialize()]))

        # keep reading while we have bytes left in the buffer
        # this allows for multiple response packets to arrive
        # so long as the board is not lollygagging returning results
        while (True):
            try:
                dr = devicebus.DumpResponse(serial_reader=bus)
            except devicebus.BusTimeoutException:
                # in this case, we cannot move further
                break

            boardExists = False

            # iterate through the boards to locate the board record
            # corresponding with the board_id from the response
            # if it does not exist, set a flag, so we can add the board
            # and in both cases we add a port record for the relevant board/port
            for board in response_dict["boards"]:
                if board["board_id"] == dr.board_id:
                    boardExists = True
                    board["ports"].append(
                        {
                            "port_index": dr.port_id,
                            "device_id": dr.device_id,
                            "device_type": devicebus.get_device_type_name(dr.data[0])
                        }
                    )
                    break;
            if not boardExists:
                response_dict["boards"].append(
                    {
                        "board_id": dr.board_id,
                        "ports": [{
                            "port_index": dr.port_id,
                            "device_id": dr.device_id,
                            "device_type": devicebus.get_device_type_name(dr.data[0])
                        }]
                    }
                )

            logger.debug(" * FLASK<<: " + str([hex(x) for x in dr.serialize()]))

        return jsonify(response_dict)


@app.route(PREFIX + __api_version__ +
           "/read/<string:deviceType>/<int:boardNum>/<int:portNum>",
           methods=['GET'])
def read_device(deviceType, boardNum, portNum):
    """ Get a device reading for the given board and port and device type.

    Args:  the deviceType corresponds to the type of device to get a reading
    for - it must match the actual type of device that is present on the bus,
    and is used to interpret the raw device reading.  The boardNum specifies
    which Pi hat to get the reading from, while the portNum specifies which port
    of the Pi hat should be polled for device reading.

    Returns:  Interpreted and raw device reading, based on the specified device
              type.

    Raises:   Returns a 500 error if the scan command fails.

    """
    with LockFile(LOCKFILE):
        bus = devicebus.initialize(app.config["SERIAL"])
        src = devicebus.DeviceReadCommand(board_id=boardNum, sequence=0x01,
                    port_id=portNum,
                    device_type=devicebus.get_device_type_code(deviceType.lower()),
                    device_id=0xFF)
        bus.write(src.serialize())

        logger.debug(" * FLASK>>: " + str([hex(x) for x in src.serialize()]))

        try:
            srr = devicebus.DeviceReadResponse(serial_reader=bus)
        except devicebus.BusTimeoutException:
            abort(500)

        logger.debug(" * FLASK<<: " + str([hex(x) for x in srr.serialize()]))

        # get raw value as number
        device_raw = ""
        try:
            for x in srr.data:
                device_raw += chr(x)
            device_raw = int(device_raw)
        except:
            abort(500)      # if we cannot convert the reading from bytes to
                            # an integer, we cannot move forward

        # convert raw value and jsonify the device reading
        if deviceType.lower() == "thermistor":
            try:
                converted_value = devicebus.convertThermistor(device_raw)
                return jsonify({"device_raw":device_raw, "temperature_c":converted_value})
            except devicebus.BusDataException:
                # if we saw an invalid value...
                abort(500)
        else:
            # for anything we don't convert, send back raw data
            # for invalid device types / device mismatches, that gets
            # caught when the request is sent over the bus
            return jsonify({"device_raw":device_raw})

@app.route(PREFIX + __api_version__ +
           "/write/<string:deviceType>/<int:boardNum>/<int:portNum>",
           methods=['GET'])
def write_device(deviceType, boardNum, portNum):
    """ Write a value to a given device (so long as the device is writeable).

    Args:  the deviceType corresponds to the type of device to write to
    - it must match the actual type of device that is present on the bus,
    and may be used to interpret the device data.  The boardNum specifies
    which Pi hat to write to, while the portNum specifies which port
    of the Pi hat should be written to.  UNDONE:  this method may change
    considerably as it has not yet been fleshed out.

    Returns:  Depends on device, but if data returned, success.

    Raises:   Returns a 500 error if the write command fails.

    """

    # not currently implemented.  we may need for the demo, but until then,
    # left undone

    abort(501)

@app.route(PREFIX + __api_version__ +
           "/power/<string:powerAction>/<int:boardNum>/<int:portNum>",
           methods=['GET'])
def power_control(powerAction, boardNum, portNum):
    """ Power on/off/cycle/status for the given board and port and device.

    Args:  powerAction may be on/off/cycle/status and corresponds to the action
    to take.  The boardNum and portNum must correspond to a device that accepts
    power control commands.

    Returns:  Power status of the given device.

    Raises:   Returns a 500 error if the power command fails.

    """
    with LockFile(LOCKFILE):
        bus = devicebus.initialize(app.config["SERIAL"])
        if powerAction.lower() == "status":
            pcc = devicebus.PowerControlCommand(board_id=boardNum, sequence=0x01,
                        port_id=portNum,
                        device_type=devicebus.get_device_type_code("power"),
                        device_id=0xFF, power_status=True)
        elif powerAction.lower() == "on":
            pcc = devicebus.PowerControlCommand(board_id=boardNum, sequence=0x01,
                        port_id=portNum,
                        device_type=devicebus.get_device_type_code("power"),
                        device_id=0xFF, power_on=True)
        elif powerAction.lower() == "off":
            pcc = devicebus.PowerControlCommand(board_id=boardNum, sequence=0x01,
                        port_id=portNum,
                        device_type=devicebus.get_device_type_code("power"),
                        device_id=0xFF, power_off=True)
        elif powerAction.lower() == "cycle":
            pcc = devicebus.PowerControlCommand(board_id=boardNum, sequence=0x01,
                        port_id=portNum,
                        device_type=devicebus.get_device_type_code("power"),
                        device_id=0xFF, power_cycle=True)
        else:
            abort(500)  # powerAction is invalid

        bus.write(pcc.serialize())

        logger.debug(" * FLASK>>: " + str([hex(x) for x in pcc.serialize()]))

        try:
            pcr = devicebus.PowerControlResponse(serial_reader=bus)
        except devicebus.BusTimeoutException:
            abort(500)

        logger.debug(" * FLASK<<: " + str([hex(x) for x in pcr.serialize()]))

        # get raw value as string
        pmbus_raw = ""
        try:
            for x in pcr.data:
                pmbus_raw += chr(x)
            # here, we should have a comma-separated string that looks like:
            # nstatus,npower,nvoltage,ncurrent
            pmbus_values = pmbus_raw.split(',')
            status_raw = int(pmbus_values[0])
            power_raw = int(pmbus_values[1])
            voltage_raw = int(pmbus_values[2])
            current_raw = int(pmbus_values[3])
        except:
            abort(500)      # if we cannot convert the reading from bytes to
                            # an integer, we cannot move forward

        def convert_power_status(raw):
            if (raw>>6 & 0x01) == 0x01:
                return "off"
            else:
                return "on"

        def bit_to_bool(raw):
            if raw == 1:
                return True
            else:
                return False

        # now, convert raw reading into subfields
        status_converted = {
            "pmbus_raw":pmbus_raw,
            "power_status":convert_power_status(status_raw),
            "power_ok":not bit_to_bool((status_raw>>11) & 0x01),
            "over_current":bit_to_bool((status_raw>>4) & 0x01),
            "under_voltage":bit_to_bool((status_raw)>>3 & 0x01),
            "input_power":devicebus.convertDirectPmbus(power_raw, "power"),
            "input_voltage":devicebus.convertDirectPmbus(voltage_raw, "voltage"),
            "output_current":devicebus.convertDirectPmbus(current_raw, "current")
        }

        return jsonify(status_converted)

def main(serial_port=SERIAL_DEFAULT, flaskdebug=False):
    """ Main method to run the flask server.

    Args:  serial_port - specify the serial port to use; the default is fine
    for production, but for testing it is necessary to pass in an emulator
    port here.  Tcp_port is the TCP port that flask should listen on.
    Flaskdebug indicates whether debug information is produced by flask.
    """
    app.config["SERIAL"] = serial_port
    app.debug = True
    if DEBUG is True:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(message)s")
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)
    if __name__ == '__main__':
        app.run(host="0.0.0.0")

if (len(sys.argv)>1):
    main(sys.argv[1])
else:
    main()
