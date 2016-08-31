#!/usr/bin/env python
"""
   OpenDCRE Southbound API Endpoint
   Author:  andrew
   Date:    4/8/2015
   Update:  6/11/2015 - Support power control commands/responses. Minor bug
                        fixes and sensor/device renaming. (ABC)
            6/19/2015 - Add locking to prevent multiple simultaneous requests
                        from stomping all over the bus.
            7/20/2015 - v0.7.0 add node information (stub for now)
            7/28/2015 - v0.7.1 convert to python package
            12/5/2015 - Line noise robustness (retries)
            2/23/2016 - Reorganize code to move IPMI and Location capabilities to other modules.
            6/20/2016 - Migrate to pyghmi for IPMI capabilities.

        \\//
         \/apor IO

Copyright (C) 2015-16  Vapor IO

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
from version import __version__      # full opendcre version
from version import __api_version__  # major.minor API version

from flask import Flask
from flask import jsonify
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

# for auth
from flask import request
from flask import Response
from functools import wraps

# for sync on the serial bus
from lockfile import LockFile

import devicebus
import vapor_common.vapor_logging as vapor_logging

from vapor_common.vapor_config import ConfigManager
from errors import *
from ipmi import *
from location import *
from uuid import getnode as get_mac_addr

# for brief delay after scan-all errors (to allow bus to continue sending data)
import time

cfg = ConfigManager('/opendcre/opendcre_config.json')

# import OpenDCRE configurations
# noinspection PyUnresolvedReferences
PREFIX = cfg.endpoint_prefix                # URL prefix for REST access
# noinspection PyUnresolvedReferences
SERIAL_DEFAULT = cfg.serial_default         # default serial device to use for bus
# noinspection PyUnresolvedReferences
LOCKFILE = cfg.lockfile                     # to prevent chaos on the serial bus
# noinspection PyUnresolvedReferences
RETRY_LIMIT = cfg.retry_limit               # number of times to retry when corrupt data is read off bus
# noinspection PyUnresolvedReferences
TIME_SLICE = cfg.time_slice                 # time slice info to be used for scan-all commands
# noinspection PyUnresolvedReferences
BMC_CONFIG = cfg.bmc_config                 # BMC configuration file for IPMI (relative path under /opendcre)

app = Flask(__name__)
logger = logging.getLogger()


# Error handler to return JSON for endpoint exceptions
def make_json_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response

for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error


################################################################################


def __count(start=0x00, step=0x01):
    """ Generator whose next() method returns consecutive values until it reaches
    0xff, then wraps back to 0x00.

    Args:
        start (int): the value at which to start the count
        step (int): the amount to increment the count

    Returns:
        An int representing the next count value.
    """
    n = start
    while True:
        yield n
        n += step
        n %= 0xff

# define a module-level counter, incremented for DeviceBusPacket sequences
_count = __count(start=0x01, step=0x01)


################################################################################


def board_id_to_hex_string(hex_value):
    """ Convenience method to convert a hexadecimal board_id value into its hex
    string representation, without the '0x' prefix, and with left-padding added
    if needed (for a 4 byte width).

    Args:
        hex_value (int): hexadecimal board id value.

    Returns:
        A string representation of the board id.
    """
    return '{0:08x}'.format(hex_value)


def device_id_to_hex_string(hex_value):
    """ Convenience method to convert a hexadecimal device_id value into its hex
    string representation, without the '0x' prefix, and with left- padding added
    if needed (for a 2 byte width).

    Args:
        hex_value (int): hexadecimal device id value.

    Returns:
        A string representation of the device id.
    """
    return '{0:04x}'.format(hex_value)


def check_valid_board_and_device(board_id=None, device_id=None):
    """ Validate that the board and device IDs are valid for the operation, and
    convert from hex string to int value for each, if valid.

    Args:
        board_id: The board_id to check.
        device_id: The device_id to check.

    Returns: (board_id, device_id) (int, int) : Integer values for board and device id.

    """
    board_id_int = check_valid_board(board_id)
    try:
        device_id_int = int(device_id, 16)
        if device_id_int < 0:
            raise ValueError("Device ID must be a positive numeric value.")
    except ValueError as e:
        logger.error("Read: Error converting device_num: %s", device_id)
        raise OpenDcreException("Error converting device_num to integer ({}).".format(e))

    return board_id_int, device_id_int


def check_valid_board(board_id=None):
    """ Validate that the board id is valid for this operation, and convert from
    hex string to int value for each, if valid.

    Args:
        board_id: The board_id to check.

    Returns: board_id (int) : Integer value of converted board_id.

    """
    try:
        board_num_int = int(board_id, 16)
        if (board_num_int > 0x00FFFFFF and not is_ipmi_board(board_num_int)) or board_num_int < 0:
            raise ValueError("Board number {} specified is out of range. Only IPMI and PLC boards with a positive ID "
                             "value may be used for this command.".format(board_id))
    except ValueError as e:
        logger.error("Version: Error converting board_num: %s.", board_id)
        raise OpenDcreException("Error converting board_num to integer ({}).".format(e))
    return board_num_int

################################################################################


def vapor_scan(packet, bus=None, retry_count=0):
    """ Query all boards and provide the active devices on each board.

    This method performs a scan operation by sending a DumpResponsePacket to
    the bus. Collisions on the bus may occur, or corrupt data may be read off
    the bus when collecting the responses. In these cases, this method employs
    a retry mechanism which first clears the bus, then re-sends the request.
    If failures continue past the configurable RETRY_LIMIT, an exception will
    be raised, indicating a problem with bus communications.

    Args:
        packet (DeviceBusPacket): the packet to send over the bus.
        bus (DeviceBus): the bus connection to send the packet over.
        retry_count (int): the number of scan retries.

    Returns:
        A dictionary containing a list of all found boards, and all devices
        found on each board.

    Raises:
        BusCommunicationError: if the number of scan retries exceed the set
            RETRY_LIMIT.
    """
    response_dict = {'boards': []}
    bus.write(packet.serialize())

    logger.debug(">>Scan: " + str([hex(x) for x in packet.serialize()]))

    try:
        response_packet = devicebus.DumpResponse(serial_reader=bus, expected_sequence=packet.sequence)
    except BusTimeoutException as e:
        raise e
    except (BusDataException, ChecksumException):
        if packet.board_id >> SCAN_ALL_BIT == 1:
            # add the shuffle bit to the packet board_id
            packet.board_id = packet.board_id | SHUFFLE_BOARD_ID
        retry_count += 1

        # flush the bus of any corrupt data
        # TODO: determine if it is necessary to wait for the timeslice to complete to flush everything out since
        # boards may still be writing
        time.sleep(0.150)
        bus.flush_all()

        # retry if permissible
        if retry_count < RETRY_LIMIT:
            logger.debug("Sending retry packet from initial.")
            return vapor_scan(packet, bus, retry_count=retry_count)
        else:
            raise BusCommunicationError('Corrupt packets received (failed checksum validation) - Retry limit reached.')
    else:
        response_dict['boards'].append({
            'board_id': board_id_to_hex_string(response_packet.board_id),
            'devices': [{
                'device_id': device_id_to_hex_string(response_packet.device_id),
                'device_type': devicebus.get_device_type_name(response_packet.data[0])
            }]
        })
        logger.debug("<<Scan: " + str([hex(x) for x in response_packet.serialize()]))

    while True:
        try:
            response_packet = devicebus.DumpResponse(serial_reader=bus, expected_sequence=packet.sequence)
        except BusTimeoutException:
            # if we get no response back from the bus, the assumption at this point is
            # that all boards/devices have been returned and there is nothing left to
            # get, so we break out of the loop and return the found results.
            break
        except (BusDataException, ChecksumException):
            if packet.board_id >> SCAN_ALL_BIT == 1:
                # add the shuffle bit to the packet board_id
                packet.board_id = packet.board_id | SHUFFLE_BOARD_ID
            retry_count += 1

            # flush the bus of any corrupt data
            # TODO: determine if it is necessary to wait for the timeslice to complete to flush everything out since
            # boards may still be writing
            time.sleep(0.150)
            bus.flush_all()

            # retry if permissible
            if retry_count < RETRY_LIMIT:
                logger.debug("Sending retry packet from retry.")
                return vapor_scan(packet, bus, retry_count=retry_count)
            else:
                raise BusCommunicationError(
                        'Corrupt packets received (failed checksum validation) - Retry limit reached.')

        else:
            board_exists = False

            # iterate through the boards to locate the board record
            # corresponding with the board_id from the response
            # if it does not exist, set a flag, so we can add the board
            # and in both cases we add a device record for the relevant board/device
            for board in response_dict['boards']:
                if int(board['board_id'], 16) == response_packet.board_id:
                    board_exists = True
                    board['devices'].append({
                        'device_id': device_id_to_hex_string(response_packet.device_id),
                        'device_type': devicebus.get_device_type_name(response_packet.data[0])
                    })
                    break

            if not board_exists:
                response_dict['boards'].append({
                    'board_id': board_id_to_hex_string(response_packet.board_id),
                    'devices': [{
                        'device_id': device_id_to_hex_string(response_packet.device_id),
                        'device_type': devicebus.get_device_type_name(response_packet.data[0])
                    }]
                })
            logger.debug("<<Scan: " + str([hex(x) for x in response_packet.serialize()]))

    # if we get here, and the scan was a scan-all and successful, we can save the scan state.
    # we don't expect a response for a save command, so after writing to the
    # bus, we can return the aggregated scan results.
    if (packet.board_id >> SCAN_ALL_BIT) & 0x01 == 0x01:
        board_id = SCAN_ALL_BOARD_ID | SAVE_BOARD_ID
        save_packet = devicebus.DumpCommand(board_id=board_id, sequence=next(_count))
        bus.write(save_packet.serialize())
        bus.flush_all()
        # TODO: verify that a brief delay is not needed here for hardware to commit

    return response_dict


################################################################################

# DEBUG METHODS

@app.route(PREFIX+__api_version__+"/test", methods=['GET', 'POST'])
def test_routine():
    """ Test routine to verify the endpoint is running and ok, without
        relying on the serial bus layer.
    """
    return jsonify({"status": "ok"})


@app.route(PREFIX+__api_version__+"/plc_config", methods=['GET', 'POST'])
def plc_config():
    """ Test routine to return the PLC modem configuration parameters on the endpoint.
    """
    with LockFile(LOCKFILE):
        if app.config['HARDWARE'] == devicebus.DEVICEBUS_RPI_HAT_V1:
            import devicebus_interfaces.plc_rpi_v1 as plc_rpi_v1
            # wake up the PLC modem
            plc_rpi_v1.wake()
            return jsonify(plc_rpi_v1.get_configuration(serial_device=app.config['SERIAL'], frequency=1))
        else:
            raise OpenDcreException("Unsupported hardware type in use. Unable to retrieve modem configuration.")

# /DEBUG METHODS


@app.route(PREFIX+__api_version__+"/version/<string:board_num>", methods=['GET'])
def get_board_version(board_num):
    """ Get board version given the specified board number.

    Args:
        board_num (str): the board number to get version for.

    Returns:
        The version of the hardware and firmware for the given board.

    Raises:
        Returns a 500 error if the version command fails.
    """
    board_num = check_valid_board(board_num)

    if is_ipmi_board(board_num):
        for bmc in app.config['BMCS']['bmcs']:
            if bmc['board_id'] == board_num:
                return jsonify({
                    'api_version': __api_version__,
                    'opendcre_version': __version__,
                    'firmware_version': 'OpenDCRE IPMI Bridge v2.0'
                })
        logger.error("Attempt to get version for invalid BMC board_num: {}".format(board_num))
        raise OpenDcreException("BMC with board_num was not found.")

    with LockFile(LOCKFILE):
        bus = devicebus.DeviceBus(hardware_type=app.config["HARDWARE"], device_name=app.config["SERIAL"])
        vc = devicebus.VersionCommand(board_id=board_num, sequence=next(_count))
        bus.write(vc.serialize())

        logger.debug(">>Version: " + str([hex(x) for x in vc.serialize()]))

        retry_count = 0
        valid_response = False
        vr = None

        try:
            vr = devicebus.VersionResponse(serial_reader=bus, expected_sequence=vc.sequence)
        except BusTimeoutException as e:
            raise OpenDcreException(e)
        except (BusDataException, ChecksumException) as e:
            while retry_count < RETRY_LIMIT and not valid_response:
                try:
                    logger.debug("Retry version board_num: %d (%s).", board_num, e.message)
                    vc = devicebus.RetryCommand(board_id=board_num, sequence=next(_count), device_id=0xFFFF,
                                                device_type=devicebus.get_device_type_code("none"))
                    logger.debug(">>Version_Retry: " + str([hex(x) for x in vc.serialize()]))
                    bus.write(vc.serialize())
                    vr = devicebus.VersionResponse(serial_reader=bus, expected_sequence=vc.sequence)
                    valid_response = True
                except (BusDataException, ChecksumException) as e:
                    logger.debug("Retry version board_num: %d (%s).", board_num, e.message)
                    retry_count += 1
                except Exception as e:
                    # if the bus times out, we are out of luck
                    # and must bail out
                    logger.exception("No response on version retry. Board: %d.", board_num)
                    raise OpenDcreException("No response on version retry. ({})".format(e))

            if retry_count == RETRY_LIMIT:
                # all of our retries fail, so we must die
                logger.error("Retry limit reached on version. Board: %d", board_num)
                raise OpenDcreException("Retry limit reached on version command.")

        logger.debug("<<Version: " + str([hex(x) for x in vr.serialize()]))

        return jsonify({"firmware_version": vr.versionString,
                        "opendcre_version": __version__,
                        "api_version": __api_version__})


@app.route(PREFIX+__api_version__+"/scan", methods=['GET'])
def scan_all():
    """ Query for all boards, and provide the active devices on each board.

    Returns:
        Active devices, numbers and types from the given board(s).

    Raises:
        Returns a 500 error if the scan command fails.
    """
    with LockFile(LOCKFILE):
        try:
            bus = devicebus.DeviceBus(hardware_type=app.config["HARDWARE"], device_name=app.config["SERIAL"])
            mac_addr = str(get_mac_addr())
            id_bytes = [int(mac_addr[i:i+2], 16) for i in range(len(mac_addr)-4, len(mac_addr), 2)]
            board_id = SCAN_ALL_BOARD_ID + (id_bytes[0] << 16) + (id_bytes[1] << 8) + TIME_SLICE
            dc = devicebus.DumpCommand(board_id=board_id, sequence=next(_count))
            response_dict = vapor_scan(dc, bus)
        except (BusDataException, BusTimeoutException, BusCommunicationError, ChecksumException) as e:
            logger.exception("Scan: Error scanning all boards.")
            raise OpenDcreException("Error scanning all boards ({}).".format(e))
        except Exception as e:
            logger.exception("Scan: Exception caught scanning all boards.")
            raise OpenDcreException("Error scanning all boards ({}).".format(e))

        # add IPMI BMC boards to results
        if 'bmcs' in app.config['BMCS']:
            for board in app.config['BMCS']['bmcs']:
                if board['board_record'] is not None:
                    response_dict['boards'].append(board['board_record'])
        return jsonify(response_dict)


@app.route(PREFIX+__api_version__+"/scan/<string:board_num>", methods=['GET'])
def get_board_devices(board_num):
    """ Query a specific board, given the board id, and provide the active
    devices on that board.

    Args:
        board_num (str): the board number to dump. If the upper byte is 0x80 then
            all boards on the bus will be scanned.

    Returns:
        Active devices, numbers and types from the given board(s).

    Raises:
        Returns a 500 error if the scan command fails.
    """
    board_num = check_valid_board(board_num)

    # check if IPMI board
    if is_ipmi_board(board_num):
        if 'bmcs' in app.config['BMCS']:
            for bmc in app.config['BMCS']['bmcs']:
                if bmc['board_id'] == board_num:
                    return jsonify({'boards': [bmc['board_record']]})
            # no bmc record
            logger.debug("Unable to find record for IPMI board: {}".format(board_num))
            raise OpenDcreException("BMC with board_num was not found.")
        else:
            # no bmc config
            logger.debug("No BMC detected while scanning IPMI board: {}".format(board_num))
            raise OpenDcreException("BMC with board_num was not found.")

    # if not IPMI board, use bus
    with LockFile(LOCKFILE):
        try:
            bus = devicebus.DeviceBus(hardware_type=app.config["HARDWARE"], device_name=app.config["SERIAL"])
            dc = devicebus.DumpCommand(board_id=board_num, sequence=next(_count))
            response_dict = vapor_scan(dc, bus)
            return jsonify(response_dict)
        except (BusDataException, BusTimeoutException, BusCommunicationError, ChecksumException) as e:
            logger.exception("Scan: Error scanning board %d.", board_num)
            raise OpenDcreException("Error scanning board ({}).".format(e))
        except Exception as e:
            logger.exception("Scan: Exception caught scanning board %d.", board_num)
            raise OpenDcreException("Error scanning board ({}).".format(e))


@app.route(PREFIX+__api_version__+"/read/<string:device_type>/<string:board_num>/<string:device_num>", methods=['GET'])
def read_device(device_type, board_num, device_num):
    """ Get a device reading for the given board and port and device type.

    We could filter on the upper ID of board_num in case an unusual board number
    is provided; however, the bus should simply time out in these cases.

    Args:
        device_type (str): corresponds to the type of device to get a reading for.
            It must match the actual type of device that is present on the bus,
            and is used to interpret the raw device reading.
        board_num (str): specifies which Pi hat to get the reading from
        device_num (str): specifies which device of the Pi hat should be polled
            for device reading.

    Returns:
        Interpreted and raw device reading, based on the specified device type.

    Raises:
        Returns a 500 error if the read command fails.
    """
    (board_num, device_num) = check_valid_board_and_device(board_num, device_num)

    # read IPMI device if applicable
    with LockFile(LOCKFILE):
        if is_ipmi_board(board_num):
            try:
                sensor_reading = read_ipmi_sensor(board_num, device_num, device_type, app.config)
                if sensor_reading is not None:
                    return jsonify(sensor_reading)
                logger.error("No response for sensor reading for board_num: {} device_num: {} type: {}".format(
                    board_num, device_num, device_type))
                raise OpenDcreException("No sensor reading returned from BMC.")
            except (IpmiException, ValueError) as e:
                logger.error("Error reading IPMI sensor: {}.".format(e.message))
                raise OpenDcreException("Error reading IPMI sensor: {}.".format(e.message))

        # otherwise we hit the bus
        bus = devicebus.DeviceBus(hardware_type=app.config["HARDWARE"], device_name=app.config["SERIAL"])
        src = devicebus.DeviceReadCommand(board_id=board_num, sequence=next(_count), device_id=device_num,
                                          device_type=devicebus.get_device_type_code(device_type.lower()))
        bus.write(src.serialize())
        bus.flush()

        logger.debug(">>Read: " + str([hex(x) for x in src.serialize()]))

        retry_count = 0
        valid_response = False
        srr = None

        try:
            srr = devicebus.DeviceReadResponse(serial_reader=bus, expected_sequence=src.sequence)
            logger.debug("<<Read: " + str([hex(x) for x in srr.serialize()]))
        except BusTimeoutException as e:
            logger.debug("No response on read device_type: %s board: %d device: %d", device_type, board_num, device_num)
            raise OpenDcreException("No response from bus on sensor read ({}).".format(e))
        except (BusDataException, ChecksumException) as e:
            while retry_count < RETRY_LIMIT and not valid_response:
                try:
                    logger.debug("Retry read device_type: %s board: %d device: %d (%s)", device_type, board_num,
                                 device_num, e.message)
                    src = devicebus.RetryCommand(board_id=board_num, sequence=next(_count), device_id=device_num,
                                                 device_type=devicebus.get_device_type_code(device_type.lower()))
                    logger.debug(">>Retry_Read: " + str([hex(x) for x in src.serialize()]))
                    bus.write(src.serialize())
                    bus.flush()
                    srr = devicebus.DeviceReadResponse(serial_reader=bus, expected_sequence=src.sequence)
                    logger.debug("<<Retry_Read: " + str([hex(x) for x in srr.serialize()]))
                    valid_response = True
                except (BusDataException, ChecksumException) as e:
                    logger.debug("Retry read device_type: %s board: %d device: %d (%s)", device_type, board_num,
                                 device_num, e.message)
                    retry_count += 1
                except Exception as e:
                    # if the bus times out, we are out of luck and must bail out
                    logger.exception("No response on retry read device_type: %s board: %d device: %d.", device_type,
                                     board_num, device_num)
                    raise OpenDcreException("No response from bus on sensor read retry ({}).".format(e))

            if retry_count == RETRY_LIMIT:
                # all of our retries fail, so we must die
                logger.error("Retry limit reached on read device_type: %s board: %d device: %d",
                             device_type, board_num, device_num)
                raise OpenDcreException("Retry limit reached on sensor read.")

    try:
        # for now, temperature is just a string->float, all else require int conversion
        if device_type.lower() == "temperature":
            device_raw = float(''.join([chr(x) for x in srr.data]))
            return jsonify({"temperature_c": device_raw})

        # for all other sensors get raw value as integer
        device_raw = int(''.join([chr(x) for x in srr.data]))

        # convert raw value and jsonify the device reading
        if device_type.lower() == "thermistor":
            converted_value = devicebus.convert_thermistor(device_raw)
            return jsonify({"temperature_c": converted_value})
        elif device_type.lower() == "humidity":
            (humidity, temperature) = devicebus.convert_humidity(device_raw)
            return jsonify({"humidity": humidity, "temperature_c": temperature})
        elif device_type.lower() == "fan_speed":
            return jsonify({"speed_rpm": device_raw})
        elif device_type.lower() == "led":
            if device_raw not in [1, 0]:
                raise ValueError("Invalid raw value returned: ({})".format(device_raw))
            state = "on" if device_raw == 1 else "off"
            return jsonify({"led_state": state})

    except (ValueError, TypeError) as e:
            # abort if unable to convert to int (ValueError), unable to convert to chr (TypeError)
            logger.exception("Read: Error converting device_raw to characters. DeviceType: %s BoardNum: %d "
                             "DeviceId: %d.", device_type, board_num, device_num)
            raise OpenDcreException("Error converting device reading ({}).".format(e))
    except Exception as e:
        # if something bad happened - all we can do is abort
        logger.exception("Read: Error converting raw value. DeviceType: %s BoardNum: %d DeviceId: %d ", device_type,
                         board_num, device_num)
        raise OpenDcreException("Error converting fan speed data ({}).".format(e))
    else:
        # for anything we don't convert, send back raw data
        # for invalid device types / device mismatches, that gets
        # caught when the request is sent over the bus
        return jsonify({"device_raw": device_raw})


@app.route(PREFIX+__api_version__+"/power/<string:board_num>/<string:device_num>/<string:power_action>",
           methods=['GET'])
@app.route(PREFIX+__api_version__ +
           "/power/<string:device_type>/<string:board_num>/<string:device_num>/<string:power_action>",
           methods=['GET'])
@app.route(PREFIX+__api_version__+"/power/<string:board_num>/<string:device_num>",
           methods=['GET'])
def power_control(power_action='status', board_num=None, device_num=None, device_type='power'):
    """ Power on/off/cycle/status for the given board and port and device.

    NOTE NOTE NOTE:  "old style" access (power/power_action/board/device) is DEPRECATED,
                     but still supported.  this will be removed in future versions.

    Args:
        power_action (str): may be on/off/cycle/status and corresponds to the
            action to take.
        board_num (str): the id of the board which contains the device that
            accepts power control commands.
        device_num (str): the id of the device which accepts power control
            commands.
        device_type (str): the type of device to accept power control command for.

    Returns:
        Power status of the given device.

    Raises:
        Returns a 500 error if the power command fails.
    """

    if board_num.lower() in ['on', 'off', 'cycle', 'status']:
        # for backwards-compatibility, we allow the command to come in as:
        # power_action/board_id/device_id  AND  board_id/device_id[/power_action]
        # therefore, if we see a new-style power action in the device_num field, then
        # we need to rearrange the parameters
        power_action_tmp = board_num
        board_num = device_num
        device_num = power_action
        power_action = power_action_tmp

    (board_num, device_num) = check_valid_board_and_device(board_num, device_num)

    # control IPMI device if applicable
    with LockFile(LOCKFILE):
        if is_ipmi_board(board_num):
            try:
                power_status = control_ipmi_power(board_num, device_num, power_action, app.config)
                if power_status is not None:
                    # power status and power ok are returned from IPMI
                    power_status["pmbus_raw"] = "0,0,0,0"
                    power_status["over_current"] = False
                    power_status["under_voltage"] = False
                    power_status["input_power"] = 0
                    power_status["input_voltage"] = 0
                    power_status["output_current"] = 0
                    return jsonify(power_status)
                logger.error("Power control attempt returned no data: board_num: {} device_num: {} action: {}".format(
                        board_num, device_num, power_action))
                raise OpenDcreException("No response from BMC for power control action.")
            except (IpmiException, ValueError) as e:
                logger.exception("Error controlling IPMI power: Board {}, Device: {}, Action: {}.".format(board_num,
                                                                                                          device_num,
                                                                                                          power_action))
                raise OpenDcreException("Error returned from BMC in controlling power via IPMI ({}).".format(e))

        bus = devicebus.DeviceBus(hardware_type=app.config["HARDWARE"], device_name=app.config["SERIAL"])
        if power_action.lower() in ["status", "on", "off", "cycle"]:
            # TODO: rectifier device support here via device_type field
            pcc = devicebus.PowerControlCommand(board_id=board_num, sequence=next(_count), device_id=device_num,
                                                device_type=devicebus.get_device_type_code("power"),
                                                power_action=power_action.lower())
        else:
            logger.error("Invalid power action received: %s", power_action)
            raise OpenDcreException("Invalid power action specified.")

        bus.write(pcc.serialize())
        logger.debug(">>Power: " + str([hex(x) for x in pcc.serialize()]))

        retry_count = 0
        valid_response = False
        pcr = None

        try:
            pcr = devicebus.PowerControlResponse(serial_reader=bus, expected_sequence=pcc.sequence)
            logger.debug("<<Power: " + str([hex(x) for x in pcr.serialize()]))
        except BusTimeoutException as e:
            logger.debug("No response on power command: %s board: %d device: %d", power_action, board_num, device_num)
            raise OpenDcreException("No response from bus on power command ({}).".format(e))
        except (BusDataException, ChecksumException) as e:
            while retry_count < RETRY_LIMIT and not valid_response:
                try:
                    logger.debug("Retry power command: %s board: %d device: %d (%s).", power_action, board_num,
                                 device_num, e.message)
                    pcc = devicebus.RetryCommand(board_id=board_num, sequence=next(_count), device_id=device_num,
                                                 device_type=devicebus.get_device_type_code("power"))
                    logger.debug(">>Retry_Power: " + str([hex(x) for x in pcc.serialize()]))
                    bus.write(pcc.serialize())
                    pcr = devicebus.PowerControlResponse(serial_reader=bus, expected_sequence=pcc.sequence)
                    valid_response = True
                    logger.debug("<<Retry_Power: " + str([hex(x) for x in pcr.serialize()]))
                except (BusDataException, ChecksumException) as e:
                    logger.debug("Retry power command: %s board: %d device: %d (%s).", power_action, board_num,
                                 device_num, e.message)
                    retry_count += 1
                except Exception as e:
                    # if the bus times out, we are out of luck
                    # and must bail out
                    logger.exception("No response on retry power command: %s board: %d device: %d.", power_action,
                                     board_num, device_num,)
                    raise OpenDcreException("No response on retry of power command ({}).".format(e))

            if retry_count == RETRY_LIMIT:
                # all of our retries fail, so we must die
                logger.error("Retry limit reached on power command: %s board: %d device: %d", power_action, board_num,
                             device_num)
                raise OpenDcreException("Retry limit reached on power command.")

        # get raw value as string
        try:
            pmbus_raw = ""
            for x in pcr.data:
                pmbus_raw += chr(x)
            # here, we should have a comma-separated string that looks like:
            # nstatus,npower,nvoltage,ncurrent
            pmbus_values = pmbus_raw.split(',')
            status_raw = int(pmbus_values[0])
            power_raw = int(pmbus_values[1])
            voltage_raw = int(pmbus_values[2])
            current_raw = int(pmbus_values[3])

            def convert_power_status(raw):
                if (raw >> 6 & 0x01) == 0x01:
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
                "pmbus_raw": pmbus_raw,
                "power_status": convert_power_status(status_raw),
                "power_ok": not bit_to_bool((status_raw >> 11) & 0x01),
                "over_current": bit_to_bool((status_raw >> 4) & 0x01),
                "under_voltage": bit_to_bool((status_raw >> 3) & 0x01),
                "input_power": devicebus.convert_direct_pmbus(power_raw, "power"),
                "input_voltage": devicebus.convert_direct_pmbus(voltage_raw, "voltage"),
                "output_current": devicebus.convert_direct_pmbus(current_raw, "current")
            }
            return jsonify(status_converted)
        except (ValueError, TypeError, IndexError) as e:
            # abort if unable to convert to int (ValueError), unable to convert
            # to chr (TypeError), or if expected pmbus_values don't exist (IndexError)
            logger.exception("Power: Error converting PMBUS data.")
            raise OpenDcreException("Error converting PMBUS data ({}).".format(e))


@app.route(PREFIX+__api_version__+"/asset/<string:board_num>/<string:device_num>",
           methods=['GET'])
def asset_info(board_num, device_num):
    """ Get asset information for a given board and device.

    Args:
        board_num: The board number to get asset information for.
        device_num: The device number to get asset information for (must be system).

    Returns: Asset information about the given device.

    """
    (board_num, device_num) = check_valid_board_and_device(board_num, device_num)

    # control IPMI device if applicable
    with LockFile(LOCKFILE):
        if is_ipmi_board(board_num):
            try:
                asset_data = get_ipmi_asset_info(board_num, device_num, app.config)
                if asset_data is not None:
                    return jsonify(asset_data)
                logger.error("No response getting asset info for board_num: {} device_num: {}".format(board_num,
                                                                                                      device_num))
                raise OpenDcreException("No response from BMC when retrieving asset information via IPMI.")
            except (IpmiException, ValueError) as e:
                logger.exception("Error getting IPMI asset info: Board {}, Device: {}.".format(board_num, device_num))
                raise OpenDcreException("Error received from BMC when retrieving asset information via IPMI ({}).".
                                        format(e))

    # PLC NOT YET AVAILABLE
    raise OpenDcreException("Asset information via PLC not supported yet.")


@app.route(PREFIX+__api_version__+"/boot_target/<string:board_num>/<string:device_num>/<string:target>",
           methods=['GET'])
@app.route(PREFIX+__api_version__+"/boot_target/<string:board_num>/<string:device_num>",
           methods=['GET'])
def boot_target(board_num, device_num, target=None):
    """ Get or set boot target for a given board and device.

    Args:
        board_num: The board number to get/set boot target for.
        device_num: The device number to get/set boot target for (must be system).
        target: The boot target to choose, or, if None, just get info.

    Returns: Boot target of the device.

    """
    (board_num, device_num) = check_valid_board_and_device(board_num, device_num)

    if target is not None and target not in ['pxe', 'hdd', 'no_override']:
        logger.error("Boot Target: Invalid boot target specified: %s board_num: %s device_num: %s", target, board_num,
                     device_num)
        raise OpenDcreException("Invalid boot target specified.")

    # control IPMI device if applicable
    with LockFile(LOCKFILE):
        if is_ipmi_board(board_num):
            try:
                if target is None:
                    boot_info = get_ipmi_boot_target(board_num, device_num, app.config)
                else:
                    action = 'no_override'
                    if target == 'no_override':
                        action = target
                    elif target == 'pxe':
                        action = target
                    elif target == 'hdd':
                        action = target
                    boot_info = set_ipmi_boot_target(board_num, device_num, action, app.config)

                if boot_info is not None:
                    return jsonify(boot_info)
                logger.error("No response for boot target operation on board_num: {} device_num: {}".format(board_num,
                                                                                                            device_num))
                raise OpenDcreException("No response from BMC on boot target operation via IPMI.")
            except (IpmiException, ValueError) as e:
                logger.exception("Error getting or setting IPMI boot target: Board {}, Device: {}, Target: {}.".format(
                        board_num, device_num, target))
                raise OpenDcreException("Error received from BMC during boot target operation via IPMI ({}).".format(e))

    # PLC NOT YET AVAILABLE
    raise OpenDcreException("Boot target operation via PLC not supported yet.")


@app.route(PREFIX+__api_version__+"/location/<string:board_num>/<string:device_num>",
           methods=['GET'])
@app.route(PREFIX+__api_version__+"/location/<string:board_num>",
           methods=['GET'])
def device_location(board_num=None, device_num=None):
    """ Get location of a device via PLC.  IPMI not supported, so unknown is returned.

    Args:
        board_num: The board number to get location for.  IPMI boards not supported.
        device_num: The device number to get location for.  IPMI devices not supported.

    Returns: Location of device.

    """
    if device_num is not None:
        (board_num, device_num) = check_valid_board_and_device(board_num, device_num)
        if device_num > 0xFFFF:
            raise OpenDcreException("Device number must be <= 0xFFFF")
    else:
        board_num = check_valid_board(board_num)

    # physical (rack) location is not yet implemented in v1
    physical_location = {"horizontal": "unknown", "vertical": "unknown", "depth": "unknown"}

    if device_num is not None:
        return jsonify({'physical_location': physical_location, 'chassis_location': get_chassis_location(device_num)})
    else:
        return jsonify({'physical_location': physical_location})


@app.route(PREFIX+__api_version__+"/led/<string:board_num>/<string:device_num>",
           methods=['GET'])
@app.route(PREFIX+__api_version__+"/led/<string:board_num>/<string:device_num>/<string:led_state>",
           methods=['GET'])
@app.route(PREFIX+__api_version__ +
           "/led/<string:board_num>/<string:device_num>/<string:led_state>/<string:led_color>",
           methods=['GET'])
def led_control(board_num, device_num, led_state=None, led_color=None):
    """ Control LED on system or wedge rack.  System led may only be turned on/off. Wedge rack supports color

    Args:
        board_num: The board number to control led for.  IPMI boards only support on/off.
        device_num: The device number to control led for.  IPMI devices only support on/off.
        led_state: The state to set LED to (on/off for IPMI, on/off/blink for PLC).
        led_color: The color to set LED to (for PLC wedge LED only).

    Returns: LED state and color (if color not known, "unknown".

    """
    # if we are reading the LED state only, forward on to the device_read method and pass along response
    if led_state is None:
        (board_num_int, device_num_int) = check_valid_board_and_device(board_num, device_num)
        if is_ipmi_board(board_num_int):
            return jsonify(get_ipmi_led_state(board_num_int, device_num_int, app.config))
        else:
            return read_device('led', board_num, device_num)

    (board_num, device_num) = check_valid_board_and_device(board_num, device_num)

    if led_state not in ['on', 'off', None]:
        logger.error("Invalid LED state {} provided for LED control.".format(led_state))
        raise OpenDcreException("Invalid LED state provided for LED control.")

    # led_color is ignored for now.
    if led_color is not None:
        logger.error("LED color setting of {} is not supported.".format(led_color))
        raise OpenDcreException("LED color setting is not supported yet.")

    # control IPMI device if applicable
    with LockFile(LOCKFILE):
        if is_ipmi_board(board_num):
            bmc_info = get_ipmi_bmc_info(board_id=board_num, config=app.config)
            if bmc_info is not None:
                if led_state is not None:
                    return jsonify(set_ipmi_led_state(board_num, device_num, led_state, app.config))
                else:
                    return jsonify(get_ipmi_led_state(board_num, device_num, app.config))
            # otherwise invalid ipmi board_id/device_id combo
            logger.error("Attempt to control LED for invalid IPMI board: {} device: {}".format(board_num, device_num))
            raise OpenDcreException("Invalid IPMI board specified for LED control.")

        # At this point we have a LED setting and valid board and device_id, so write to the devicebus
        # note: vapor_led control is not yet supported
        led_state = '1' if led_state == 'on' else '0'
        bus = devicebus.DeviceBus(hardware_type=app.config["HARDWARE"], device_name=app.config["SERIAL"])
        dwc = devicebus.DeviceWriteCommand(board_id=board_num, sequence=next(_count), device_id=device_num,
                                           device_type=devicebus.get_device_type_code('led'),
                                           raw_data=led_state)
        bus.write(dwc.serialize())
        bus.flush()

        logger.debug(">>Write: " + str([hex(x) for x in dwc.serialize()]))

        retry_count = 0
        valid_response = False
        dwr = None

        try:
            dwr = devicebus.DeviceWriteResponse(serial_reader=bus, expected_sequence=dwc.sequence)
            logger.debug("<<Write: " + str([hex(x) for x in dwr.serialize()]))
        except BusTimeoutException as e:
            logger.debug("No response on read device_type: %s board: %d device: %d", 'led', board_num, device_num)
            raise OpenDcreException("No response from bus on sensor read ({}).".format(e))
        except (BusDataException, ChecksumException) as e:
            while retry_count < RETRY_LIMIT and not valid_response:
                try:
                    logger.debug("Retry write device_type: %s board: %d device: %d (%s)", 'led', board_num,
                                 device_num, e.message)
                    dwc = devicebus.RetryCommand(board_id=board_num, sequence=next(_count), device_id=device_num,
                                                 device_type=devicebus.get_device_type_code('led'))
                    logger.debug(">>Retry_Write: " + str([hex(x) for x in dwc.serialize()]))
                    bus.write(dwc.serialize())
                    bus.flush()
                    dwr = devicebus.DeviceReadResponse(serial_reader=bus, expected_sequence=dwc.sequence)
                    logger.debug("<<Retry_Write: " + str([hex(x) for x in dwr.serialize()]))
                    valid_response = True
                except (BusDataException, ChecksumException) as e:
                    logger.debug("Retry read device_type: %s board: %d device: %d (%s)", 'led', board_num,
                                 device_num, e.message)
                    retry_count += 1
                except Exception as e:
                    # if the bus times out, we are out of luck and must bail out
                    logger.exception("No response on retry read device_type: %s board: %d device: %d.", 'led',
                                     board_num, device_num)
                    raise OpenDcreException("No response from bus on sensor read retry ({}).".format(e))

            if retry_count == RETRY_LIMIT:
                # all of our retries fail, so we must die
                logger.error("Retry limit reached on read device_type: %s board: %d device: %d",
                             'led', board_num, device_num)
                raise OpenDcreException("Retry limit reached on sensor read.")

    # get raw value to ensure remote device took the write.
    try:
        device_raw = str(''.join([chr(x) for x in dwr.data]))
    except (ValueError, TypeError) as e:
        # abort if unable to convert to int (ValueError), unable to convert to chr (TypeError)
        logger.exception("Read: Error converting device_raw to characters. DeviceType: %s BoardNum: %d "
                         "DeviceId: %d.", 'led', board_num, device_num)
        raise OpenDcreException("Error converting device reading ({}).".format(e))
    if device_raw == 'W1':
        return read_device('led', str(hex(board_num)), str(hex(device_num)))
    else:
        raise OpenDcreException("Error writing to device.")


@app.route(PREFIX+__api_version__+"/fan/<string:board_num>/<string:device_num>",
           methods=['GET'])
@app.route(PREFIX+__api_version__+"/fan/<string:board_num>/<string:device_num>/<string:fan_speed>",
           methods=['GET'])
def fan_control(board_num, device_num, fan_speed=None):
    """ Control fan on system or Vapor Chamber.  System fan may only be polled for status
    unless explicitly supported.

    Args:
        board_num: The board number to control led for.  IPMI boards only support on/off.
        device_num: The device number to control led for.  IPMI devices only support on/off.
        fan_speed: The speed to set fan to (on/off for IPMI, on/off/blink for PLC).

    Returns: LED state and color (if color not known, "unknown".

    """
    # if we are reading the fan speed only, forward on to the device_read method and pass along response
    if fan_speed is None:
        (board_num_int, device_num_int) = check_valid_board_and_device(board_num, device_num)
        if is_ipmi_board(board_num_int):
                return jsonify(read_ipmi_sensor(board_num_int, device_num_int, 'fan_speed', app.config))
        else:
                return read_device('fan_speed', board_num, device_num)

    (board_num, device_num) = check_valid_board_and_device(board_num, device_num)

    if fan_speed is not None:
        try:
            fan_speed_int = int(fan_speed)
            if MAX_FAN_SPEED < fan_speed_int or MIN_FAN_SPEED > fan_speed_int:
                raise ValueError("Fan speed out of acceptable range.")
        except ValueError as e:
            logger.error("Location: Error converting fan_speed: %s", str(fan_speed))
            raise OpenDcreException("Error converting fan_speed to integer ({}).".format(e))

    # control IPMI device if applicable
    with LockFile(LOCKFILE):
        if is_ipmi_board(board_num):
            bmc_info = get_ipmi_bmc_info(board_id=board_num, config=app.config)
            if bmc_info is not None:
                if fan_speed is not None:
                    raise OpenDcreException("Setting of fan speed for this device is not permitted.")
                else:
                    return jsonify(read_ipmi_sensor(board_num, device_num, 'fan_speed', app.config))
            # otherwise invalid ipmi board_id/device_id combo
            logger.error("Attempt to control fan for invalid IPMI board: {} device: {}".format(board_num, device_num))
            raise OpenDcreException("Invalid IPMI board specified for fan control.")

        # At this point we have a fan speed and valid board and device_id, so write to the devicebus
        bus = devicebus.DeviceBus(hardware_type=app.config["HARDWARE"], device_name=app.config["SERIAL"])
        dwc = devicebus.DeviceWriteCommand(board_id=board_num, sequence=next(_count), device_id=device_num,
                                           device_type=devicebus.get_device_type_code('fan_speed'),
                                           raw_data=fan_speed)
        bus.write(dwc.serialize())
        bus.flush()

        logger.debug(">>Write: " + str([hex(x) for x in dwc.serialize()]))

        retry_count = 0
        valid_response = False
        dwr = None

        try:
            dwr = devicebus.DeviceWriteResponse(serial_reader=bus, expected_sequence=dwc.sequence)
            logger.debug("<<Write: " + str([hex(x) for x in dwr.serialize()]))
        except BusTimeoutException as e:
            logger.debug("No response on read device_type: %s board: %d device: %d", 'fan_speed', board_num, device_num)
            raise OpenDcreException("No response from bus on sensor read ({}).".format(e))
        except (BusDataException, ChecksumException) as e:
            while retry_count < RETRY_LIMIT and not valid_response:
                try:
                    logger.debug("Retry write device_type: %s board: %d device: %d (%s)", 'fan_speed', board_num,
                                 device_num, e.message)
                    dwc = devicebus.RetryCommand(board_id=board_num, sequence=next(_count), device_id=device_num,
                                                 device_type=devicebus.get_device_type_code('fan_speed'))
                    logger.debug(">>Retry_Write: " + str([hex(x) for x in dwc.serialize()]))
                    bus.write(dwc.serialize())
                    bus.flush()
                    dwr = devicebus.DeviceReadResponse(serial_reader=bus, expected_sequence=dwc.sequence)
                    logger.debug("<<Retry_Write: " + str([hex(x) for x in dwr.serialize()]))
                    valid_response = True
                except (BusDataException, ChecksumException) as e:
                    logger.debug("Retry read device_type: %s board: %d device: %d (%s)", 'fan_speed', board_num,
                                 device_num, e.message)
                    retry_count += 1
                except Exception as e:
                    # if the bus times out, we are out of luck and must bail out
                    logger.exception("No response on retry read device_type: %s board: %d device: %d.", 'fan_speed',
                                     board_num, device_num)
                    raise OpenDcreException("No response from bus on sensor read retry ({}).".format(e))

            if retry_count == RETRY_LIMIT:
                # all of our retries fail, so we must die
                logger.error("Retry limit reached on read device_type: %s board: %d device: %d",
                             'fan_speed', board_num, device_num)
                raise OpenDcreException("Retry limit reached on sensor read.")

    # get raw value to ensure remote device took the write.
    try:
        device_raw = str(''.join([chr(x) for x in dwr.data]))
    except (ValueError, TypeError) as e:
        # abort if unable to convert to int (ValueError), unable to convert to chr (TypeError)
        logger.exception("Read: Error converting device_raw to characters. DeviceType: %s BoardNum: %d "
                         "DeviceId: %d.", 'fan_speed', board_num, device_num)
        raise OpenDcreException("Error converting device reading ({}).".format(e))
    if device_raw == 'W1':
        return read_device('fan_speed', str(hex(board_num)), str(hex(device_num)))
    else:
        raise OpenDcreException("Error writing to device.")


def main(serial_port=SERIAL_DEFAULT, hardware=devicebus.DEVICEBUS_EMULATOR_V1):
    """ Main method to run the flask server.

    Args:
        serial_port (str): specify the serial port to use; the default is fine
            for production, but for testing it is necessary to pass in an emulator
            port here.
        hardware (int): the type of hardware we are working with - see devicebus.py
            for values -> by default we use the emulator, but may use VEC or RPI HAT
            which dictates what type of configuration we do on startup and throughout.
    """
    app.config['SERIAL'] = serial_port
    app.config['HARDWARE'] = int(hardware)

    vapor_logging.setup_logging(default_path='logging_core.json')

    logger.info("========================================")
    logger.info("Starting OpenDCRE Southbound Endpoint.")
    logger.info("Hardware device: (%s).", app.config['SERIAL'])
    logger.info("Hardware type: (%d).", app.config['HARDWARE'])
    if app.config['HARDWARE'] == devicebus.DEVICEBUS_RPI_HAT_V1:
        for x in range(2):
            logger.info("Configuring hardware.")
            import devicebus_interfaces.plc_rpi_v1 as plc_rpi_v1
            # wake up the PLC modem
            plc_rpi_v1.wake()
            plc_rpi_v1.configure(app.config['SERIAL'], plc_rpi_v1.OPENDCRE_DEFAULT_CONFIGURATION)

    logger.info("Scanning IPMI BMCs.")
    app.config["BMCS"] = scan_ipmi(config_file=BMC_CONFIG)
    num_bmcs = 0 if 'bmcs' not in app.config["BMCS"] else len(app.config['BMCS']['bmcs'])
    logger.info("%d BMCs found. Starting endpoint.", num_bmcs)

    if __name__ == '__main__':
        app.run(host="0.0.0.0")
