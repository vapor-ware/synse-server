#!/usr/bin/env python
""" Synse Device Bus Test Emulator.

    Author:  andrew
    Date:    4/16/2015
    Updated: 6/11/2015 - Add power control/status commands (andrew)
             12/4/2015 - Add retry logic support (andrew)

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

This file is part of Synse.

Synse is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

Synse is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Synse.  If not, see <http://www.gnu.org/licenses/>.
"""
import json
import logging
import sys

import vapor_common.vapor_logging as vapor_logging
from synse.definitions import SCAN_ALL_BIT, SAVE_BIT, SHUFFLE_BIT
from synse.utils import *
from synse.devicebus.devices.plc.plc_bus import *

logger = logging.getLogger(__name__)

emulator_config = dict()

TERMINATE = False  # set to true to shut down the emulator
configuration = {}  # where our emulator configuration will live

SEQUENCE_NUMBER_SENTINEL = 999      # when encountered, replace with the desired sequence number
CHECKSUM_SENTINEL = 1000            # mask for checksum, remainder is offset of starting byte of checksum

"""
    This emulator is designed to stand-in for the actual Synse device Bus
    Pi Hat hardware, which is addressable via serial communications.

    The emulator takes as its first parameter the name of the TTY (PTY) device
    that will communicate with an upper level client (e.g. the Synse API
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

    IMPORTANT ADDENDUM 1/18/2016:  The emulator also may be used with PLC comms,
        (without socat).  To run the emulator, run start_vapor_core_emulator.sh
        with the parameters to the TTY, configuration file (e.g. simple.json),
        and hardware type.

    Enjoy.
"""


# ==============================================================================#
#                         Emulator Convenience Methods                          #
# ==============================================================================#


def board_ids_match(config_board, dev_bus_cmd):
    """ Check that the configuration board id matches the command's board id.

    Convenience method to check that the configuration's board id matches the
    board id from the devicebus command. this requires a type conversion, since
    the config's board id is a hex-string and the devicebus command's board id
    is a hexadecimal value.

    Args:
        config_board: The board in the configuration.
        dev_bus_cmd: The devicebus command holding the board id.

    Returns: 
        bool: True if they match, False otherwise.
    """
    return int(config_board['board_id'], 16) == dev_bus_cmd.board_id


def device_ids_match(config_device, dev_bus_cmd):
    """ Check that the configuration device id matches the command's device id.

    Convenience method to check that the configuration's device id matches the
    device id from the devicebus command. this requires a type conversion, since
    the config's device id is a hex-string and the devicebus command's device id
    is a hexadecimal value.

    Args:
        config_device: The device id from config.
        dev_bus_cmd: The devicebus command holding the device id.

    Returns: 
        bool: True if they match, False otherwise.
    """
    return int(config_device['device_id'], 16) == dev_bus_cmd.device_id


def device_types_compatible(config_device, dev_bus_cmd):
    """ Check that the configuration device type is compatible with the command's device type.

    Convenience method to check that the configuration's device type matches the
    device type from the devicebus command.

    Args:
        config_device: The device id from config.
        dev_bus_cmd: The devicebus command holding the device type.

    Returns: 
        bool: True if they match, False otherwise.
    """
    if get_device_type_name(dev_bus_cmd.device_type) == 'fan_speed':
        return config_device['device_type'] in ['vapor_fan', 'fan_speed']
    else:
        return get_device_type_name(dev_bus_cmd.device_type) == config_device['device_type']


# ==============================================================================#
#                                Emulator Main                                  #
# ==============================================================================#

def generate_emulator_checksum(raw_bytes, start, end):
    """ Convenience method for generating a checksum over a raw byte range.
    Redundant to what is in devicebus, but added in this form for simplicity.

    Args:
        raw_bytes (list): the byte buffer to compute checksum for.
        start (int): the starting index of the buffer.
        end (int): the ending index of the buffer to checksum.

    Returns: 
        int: the checksum over the specified buffer range.
    """
    checksum = 0
    for x in raw_bytes[start:end]:
        checksum = checksum + x
    twoscomp = ((~checksum) + 1) & 0xFF
    return twoscomp


def transform_raw(raw_bytes, seq_no):
    """ Transforms raw_bytes into a proper byte stream for sending over the bus.
    This includes replacing the SEQ_NO_SENTINEL with the sequence number, and also
    computing the correct checksum if the CK_SENTINEL is present.

    Args:
        raw_bytes (list): the raw byte stream from the emulator config.
        seq_no (int): the sequence number to drop in.

    Returns: 
        list: a transformed list of bytes based on the input.
    """
    # copy bytes so we do not stomp the emulator config for later uses of the
    # same bytes (otherwise, on the first use, the sentinels are removed for the lifetime of the emulator)
    new_bytes = list(raw_bytes)
    for i, x in enumerate(new_bytes):
        if x == SEQUENCE_NUMBER_SENTINEL:
            new_bytes[i] = seq_no
        elif CHECKSUM_SENTINEL <= x <= CHECKSUM_SENTINEL + 255:
            new_bytes[i] = generate_emulator_checksum(new_bytes, x - CHECKSUM_SENTINEL, i)
    return new_bytes


def inject_error(raw_bytes):
    """ Inject an error in a serialized devicebus packet by messing up the data
    within by adding 1 to each byte. The header and trailer are not affected,
    but the bytes within the packet are.

    Args:
        raw_bytes (list): the raw bytes to inject an error into.

    Returns: 
        list: a transformed list of raw bytes with erroneous data within.
    """
    for i in range(len(raw_bytes)):
        if raw_bytes[i] != PKT_VALID_HEADER and raw_bytes[i] != PKT_VALID_TRAILER:
            raw_bytes[i] = (raw_bytes[i] + 1) % 255
    return raw_bytes


def main(emulator_device):
    """ The main emulator control loop. Runs until it is time to stop.

    Args:
        emulator_device (str): the serial port device name (e.g. /dev/ttyVapor002
            or /dev/ttyAMA0) to listen on.
    """
    emulator = DeviceBus(hardware_type=DEVICEBUS_EMULATOR_V1, device_name=emulator_device, timeout=None)
    prev_packet = None
    is_retry = False

    while not TERMINATE:
        # retrieve packet from client
        try:
            packet = DeviceBusPacket(serial_reader=emulator)
            sequence = packet.sequence  # to be plumbed into all non-static packets sent back
            logger.debug('<<Packet ' + str([hex(x) for x in packet.serialize()]))
        except Exception as ex:
            logger.error('Exception encountered deserializing packet (%s).', ex)
            return

        # grab command from packet data
        cmd = chr(packet.data[0])
        logger.debug('Packet Command: {}'.format(cmd))

        # check for retry request first
        if cmd == '?':
            packet = prev_packet  # determine what is being retried
            is_retry = True  # set to indicate should retry request
            cmd = chr(packet.data[0])  # get the command out of the prev req
            logger.debug('Retry Encountered - Command (%s)', cmd)

        # handle command from packet
        if cmd == 'D':
            # ======================> SCAN <======================
            sc = DumpCommand(data_bytes=packet.serialize())
            # if the save bit is enabled in the board_id, do nothing, since we
            # expect no response back in this case.
            if (sc.board_id >> SAVE_BIT) & 0x01 == 1:
                logger.debug('Encountered Save Bit')
            else:
                # match sc.board_id against a board_id in configuration - if
                # the board_id does not exist, send nothing; if board_id is 0xFF
                # return all boards unless we are emulating early firmware not
                # supporting scan-all-boards, where we instead return nothing
                if (sc.board_id >> SCAN_ALL_BIT) & 0x01 != 1:
                    for board in configuration['boards']:
                        if board_ids_match(board, sc):
                            if is_retry:
                                if 'retry_raw_data' in board:
                                    # now we can craft a response
                                    responses_length = len(board['retry_raw_data'])
                                    # get the responses counter
                                    _retry_count = board['_retry_scan_count'] if '_retry_scan_count' in board else 0

                                    if responses_length > 0 and _retry_count < responses_length:
                                        if isinstance(board['retry_raw_data'][_retry_count], list):
                                            # we are sending raw bytes
                                            logger.debug('>>Scan: ' + str([hex(x) for x in transform_raw(
                                                raw_bytes=board['retry_raw_data'][_retry_count], seq_no=sequence)]))
                                            emulator.write(transform_raw(board['retry_raw_data'][_retry_count],
                                                                         seq_no=sequence))
                                            emulator.flush()
                                        else:
                                            # otherwise, we do not send a response
                                            pass
                                        # now increment index into our responses, and wrap it if
                                        # we are repeatable
                                        _retry_count += 1
                                        _retry_count %= len(board['retry_raw_data'])
                                        board['_retry_scan_count'] = _retry_count
                                        pass
                            else:
                                if 'raw_data' in board:
                                    # now we can craft a response
                                    responses_length = len(board['raw_data'])
                                    # get the responses counter
                                    _scan_count = board['_scan_count'] if '_scan_count' in board else 0

                                    if responses_length > 0 and _scan_count < responses_length:
                                        if isinstance(board['raw_data'][_scan_count], list):
                                            for packet in board['raw_data'][_scan_count]:
                                                # we are sending raw bytes
                                                logger.debug('>>Scan: ' + str([hex(x) for x in
                                                                               transform_raw(raw_bytes=packet,
                                                                                             seq_no=sequence)]))
                                                emulator.write(transform_raw(raw_bytes=packet, seq_no=sequence))
                                                emulator.flush()
                                        else:
                                            # otherwise, we do not send a response
                                            pass
                                        # now increment index into our responses, and wrap it if
                                        # we are repeatable
                                        _scan_count += 1
                                        _scan_count %= len(board['raw_data'])
                                        board['_scan_count'] = _scan_count
                                        pass
                                else:
                                    for device in board['devices']:
                                        srp = DumpResponse(
                                            board_id=board['board_id'],
                                            sequence=sequence,
                                            device_id=device['device_id'],
                                            device_type=get_device_type_code(device['device_type']),
                                            data=[get_device_type_code(device['device_type'])]
                                        )
                                        logger.debug('>>Scan: ' + str([hex(x) for x in srp.serialize()]))
                                        emulator.write(srp.serialize())
                                        emulator.flush()
                                        # we have sent everything from this board
                # SCAN ALL
                else:
                    # first check if 'scanall' key in configuration
                    # if it is, establish as _scanall_count
                    # next, check the bits - if this is a pure scanall,
                    # without the shuffle bit set, this is our initial
                    # scanall, so do what is required in terms of returning ok or error results
                    # else if this is a shuffle, check for a _scanall_retry_count value
                    # and establish or process based on configuration for that count
                    # and, as noted above, if the save bit is set, we already skip as all's well.

                    failed_board = None     # only set if a failure is expected
                    if 'scanall' in configuration:
                        _scanall_count = configuration['_scanall_count'] if '_scanall_count' in configuration else 0
                        logger.debug('SCANALL COUNT : {}'.format(_scanall_count))
                        if (sc.board_id >> SHUFFLE_BIT) & 0x01 == 0:
                            # this is an initial attempt
                            if configuration['scanall'][_scanall_count]['initial']['result'] == 'error':
                                failed_board = configuration['scanall'][_scanall_count]['initial']['failed_board']
                                logger.debug('>> Scanall: Returning results with bad board {}.'.format(failed_board))
                            # otherwise, return everything as specified in the config
                            else:
                                logger.debug('>> Scanall: Returning all results without error.')
                                # advance to the next scan test
                                _scanall_count += 1
                                _scanall_count %= len(configuration['scanall'])
                                configuration['_scanall_count'] = _scanall_count
                                logger.debug('SCANALL COUNT INCREMENTED : {}'.format(_scanall_count))
                            pass
                        else:
                            # this is a shuffle attempt
                            _scanall_retry_count = \
                                configuration['scanall'][_scanall_count]['_scanall_retry_count'] \
                                if '_scanall_retry_count' in configuration['scanall'][_scanall_count] else 0
                            logger.debug('SCANALL RETRY COUNT {}'.format(_scanall_retry_count))
                            if configuration['scanall'][_scanall_count]['retry'][_scanall_retry_count]['result'] \
                                    == 'error':
                                failed_board = \
                                    configuration[
                                        'scanall'][_scanall_count]['retry'][_scanall_retry_count]['failed_board']
                                logger.debug(
                                    '>> Scanall retry: Returning results with bad board {}.'.format(failed_board))
                            else:
                                # otherwise, return everything as specified in the config
                                logger.debug('>> Scanall retry: Returning all results without error.')
                            _scanall_retry_count += 1
                            logger.debug('SCANALL RETRY COUNT INCREMENTED : {}'.format(_scanall_retry_count))
                            configuration['scanall'][_scanall_count]['_scanall_retry_count'] = _scanall_retry_count
                            if _scanall_retry_count == len(configuration['scanall'][_scanall_count]['retry']):
                                # advance to the next scan test
                                _scanall_count += 1
                                _scanall_count %= len(configuration['scanall'])
                                configuration['_scanall_count'] = _scanall_count
                                logger.debug('RESETTING SCANALL COUNT {}'.format(_scanall_count))

                    # at this point, if failed_board is not None, we need to muck up the results from failed_board -
                    # all other results will return fine
                    for board in configuration['boards']:
                        if is_retry:
                            if 'retry_raw_data' in board:
                                rsp_bytes = transform_raw(raw_bytes=board['retry_raw_data'], seq_no=sequence)
                                if board['board_id'] == failed_board:
                                    rsp_bytes = inject_error(rsp_bytes)
                                logger.debug('>>Scan: ' + str([hex(x) for x in rsp_bytes]))
                                emulator.write(rsp_bytes)
                                emulator.flush()
                        else:
                            if 'raw_data' in board:
                                # now we can craft a response
                                responses_length = len(board['raw_data'])
                                # get the responses counter
                                _scan_count = board['_scan_count'] if '_scan_count' in board else 0

                                if responses_length > 0 and _scan_count < responses_length:
                                    if isinstance(board['raw_data'][_scan_count], list):
                                        for packet in board['raw_data'][_scan_count]:
                                            # we are sending raw bytes
                                            rsp_bytes = transform_raw(raw_bytes=packet, seq_no=sequence)
                                            if board['board_id'] == failed_board:
                                                rsp_bytes = inject_error(rsp_bytes)
                                            logger.debug('>>Scan: ' + str([hex(x) for x in rsp_bytes]))
                                            emulator.write(rsp_bytes)
                                            emulator.flush()
                                    else:
                                        # otherwise, we do not send a response
                                        pass
                                    # now increment index into our responses, and wrap it if
                                    # we are repeatable
                                    _scan_count += 1
                                    _scan_count %= len(board['raw_data'])
                                    board['_scan_count'] = _scan_count
                                    pass
                            else:
                                for device in board['devices']:
                                    srp = DumpResponse(
                                        board_id=board['board_id'],
                                        sequence=sequence,
                                        device_id=device['device_id'],
                                        device_type=get_device_type_code(device['device_type']),
                                        data=[get_device_type_code(device['device_type'])]
                                    )
                                    rsp_bytes = srp.serialize()
                                    if board['board_id'] == failed_board:
                                        logger.debug('Injecting bad bytes to response.')
                                        rsp_bytes = inject_error(rsp_bytes)
                                    logger.debug('>>Scan: ' + str([hex(x) for x in rsp_bytes]))
                                    emulator.write(rsp_bytes)
                                    emulator.flush()
                # if we get here, nothing to send
                pass

        elif cmd == 'V':
            # ======================> VERSION <======================
            # TODO: support a collection of versions in the schema
            vc = VersionCommand(data_bytes=packet.serialize())
            for board in configuration['boards']:
                if board_ids_match(board, vc):
                    if is_retry:
                        if 'retry_firmware_version' in board:
                            # now we can craft a response
                            responses_length = len(board['retry_firmware_version'])
                            # get the responses counter
                            _retry_count = board['_retry_version_count'] if '_retry_version_count' in board else 0

                            if responses_length > 0 and _retry_count < responses_length:
                                if isinstance(board['retry_firmware_version'][_retry_count], list):
                                    # we are sending raw bytes
                                    logger.debug('>>Version: ' + str([hex(x) for x in transform_raw(
                                        raw_bytes=board['retry_firmware_version'][_retry_count],
                                        seq_no=sequence)]))
                                    emulator.write(
                                        transform_raw(raw_bytes=board['retry_firmware_version'][_retry_count],
                                                      seq_no=sequence))
                                    emulator.flush()
                                else:
                                    # otherwise, we do not send a response
                                    pass
                                # now increment index into our responses, and wrap it if
                                # we are repeatable
                                _retry_count += 1
                                _retry_count %= len(board['retry_firmware_version'])
                                board['_retry_version_count'] = _retry_count
                                pass
                    else:
                        if isinstance(board['firmware_version'], list):
                            # sending raw bytes
                            logger.debug('>>Version: ' + str([hex(x) for x in
                                                              transform_raw(raw_bytes=board['firmware_version'],
                                                                            seq_no=sequence)]))
                            emulator.write(transform_raw(raw_bytes=board['firmware_version'], seq_no=sequence))
                            emulator.flush()
                        else:
                            vr = VersionResponse(
                                sequence=sequence,
                                version_string=board['firmware_version']
                            )  # TODO: set board_id field?
                            logger.debug('>>Version: ' + str([hex(x) for x in vr.serialize()]))
                            emulator.write(vr.serialize())
                            emulator.flush()
                            # otherwise, no response

        elif cmd == 'R':
            # ======================> READ <======================
            # first, determine what kind of a read we are dealing with
            if len(packet.data) == 1:
                # data -> ['R'] : Read Command
                rc = DeviceReadCommand(data_bytes=packet.serialize())
                for board in configuration['boards']:
                    if board_ids_match(board, rc):
                        for device in board['devices']:
                            if device_ids_match(device, rc) and device_types_compatible(device, rc) \
                                    and ('read' in device):
                                if is_retry and ('retry_responses' in device['read']):
                                    # now we can craft a response
                                    responses_length = len(device['read']['retry_responses'])
                                    # get the responses counter
                                    _retry_count = device['read']['_retry_count'] if '_retry_count' in \
                                                                                     device['read'] else 0

                                    if responses_length > 0 and _retry_count < responses_length:
                                        if isinstance(device['read']['retry_responses'][_retry_count], list):
                                            # we are sending raw bytes
                                            logger.debug('>>Read: ' + str(
                                                [hex(x) for x in transform_raw(
                                                    raw_bytes=device['read']['retry_responses'][_retry_count],
                                                    seq_no=sequence)]))
                                            emulator.write(transform_raw(
                                                raw_bytes=device['read']['retry_responses'][_retry_count],
                                                seq_no=sequence))
                                            emulator.flush()
                                        else:
                                            # otherwise, we do not send a response
                                            pass
                                        # now increment index into our responses, and wrap it if
                                        # we are repeatable
                                        _retry_count += 1
                                        _retry_count %= len(device['read']['retry_responses'])
                                        device['read']['_retry_count'] = _retry_count
                                        pass
                                else:
                                    if 'has_state' in device and device['has_state']:
                                        device['_state'] = device['_state'] if '_state' in device else \
                                            device['read']

                                        reading = [ord(x) for x in str(device['_state'])]
                                        rr = DeviceReadResponse(device_reading=reading, sequence=sequence)
                                        logger.debug('>>Read: ' + str([hex(x) for x in rr.serialize()]))
                                        emulator.write(rr.serialize())
                                        emulator.flush()
                                        pass
                                    else:
                                        # now we can craft a response
                                        responses_length = len(device['read']['responses'])
                                        # get the responses counter
                                        _count = device['read']['_count'] if '_count' in device['read'] else 0

                                        if responses_length > 0 and _count < responses_length:
                                            if isinstance(device['read']['responses'][_count], list):
                                                # we are sending raw bytes
                                                logger.debug('>>Read: ' + str(
                                                    [hex(x) for x in transform_raw(
                                                        raw_bytes=device['read']['responses'][_count],
                                                        seq_no=sequence)]))
                                                emulator.write(transform_raw(
                                                    raw_bytes=device['read']['responses'][_count],
                                                    seq_no=sequence))
                                                emulator.flush()
                                            elif device['read']['responses'][_count] is not None:
                                                # we are sending back a device reading
                                                reading = [ord(x) for x in str(device['read']['responses'][_count])]
                                                rr = DeviceReadResponse(device_reading=reading, sequence=sequence)
                                                logger.debug('>>Read: ' + str([hex(x) for x in rr.serialize()]))
                                                emulator.write(rr.serialize())
                                                emulator.flush()
                                            else:
                                                # otherwise, we do not send a response
                                                pass
                                            # now increment index into our responses, and wrap it if
                                            # we are repeatable
                                            _count += 1
                                            if device['read']['repeatable']:
                                                _count %= len(device['read']['responses'])
                                            device['read']['_count'] = _count
                                            pass
        elif cmd == 'P':
            # ======================> POWER CONTROL <======================
            # the second character of packet.data is the actual command/action
            pc = PowerControlCommand(data_bytes=packet.serialize())

            # return power status regardless of command - users of the emulator
            # should design the config tests to match the anticipated sequence
            # of commands/requests
            for board in configuration['boards']:
                if board_ids_match(board, pc):
                    for device in board['devices']:
                        if device_ids_match(device, pc) and (
                                device['device_type'] in ['vapor_rectifier', 'power', 'vapor_battery'] and (
                                'power' in device)):
                            if is_retry and ('retry_responses' in device['power']):
                                # now we can craft a response
                                responses_length = len(device['power']['retry_responses'])
                                # get the responses counter
                                _retry_count = device['power']['_retry_count'] if '_retry_count' in device[
                                    'power'] else 0

                                if responses_length > 0 and _retry_count < responses_length:
                                    if isinstance(device['power']['retry_responses'][_retry_count], list):
                                        # we are sending raw bytes
                                        logger.debug('>>Power: ' + str([hex(x) for x in transform_raw(
                                            raw_bytes=device['power']['retry_responses'][_retry_count],
                                            seq_no=sequence)]))
                                        emulator.write(transform_raw(
                                            raw_bytes=device['power']['retry_responses'][_retry_count],
                                            seq_no=sequence))
                                        emulator.flush()
                                    else:
                                        # otherwise, we do not send a response
                                        pass
                                    # now increment index into our responses, and wrap it if
                                    # we are repeatable
                                    _retry_count += 1
                                    _retry_count %= len(device['power']['retry_responses'])
                                    device['power']['_retry_count'] = _retry_count
                                    pass
                            else:
                                if 'has_state' in device and device['has_state']:
                                    device['_state'] = device['_state'] if '_state' in device else \
                                        device['power']

                                    # toggle device state based on incoming command
                                    # if a ? command, don't do anything, just return existing state
                                    if chr(int(pc.data[1])) == '0':
                                        device['_state'] = device['off']
                                    elif chr(int(pc.data[1])) == '1':
                                        device['_state'] = device['on']

                                    if isinstance(device['_state'], list):
                                        _count = device['_count'] if '_count' in device else 0
                                        power_status = [ord(x) for x in str(device['_state'][_count])]
                                        _count += 1
                                        _count %= len(device['_state'])
                                        device['_count'] = _count
                                    else:
                                        power_status = [ord(x) for x in str(device['_state'])]

                                    pr = PowerControlResponse(data=power_status, sequence=sequence)
                                    logger.debug('>>Power: ' + str([hex(x) for x in pr.serialize()]))
                                    emulator.write(pr.serialize())
                                    emulator.flush()
                                    pass
                                else:
                                    responses_length = len(device['power']['responses'])
                                    # get the responses counter
                                    _count = device['power']['_count'] if '_count' in device['power'] else 0

                                    if responses_length > 0 and _count < responses_length:
                                        if isinstance(device['power']['responses'][_count], list):
                                            # we are sending raw bytes
                                            logger.debug('>>Power: ' + str([hex(x) for x in transform_raw(
                                                raw_bytes=device['power']['responses'][_count],
                                                seq_no=pc.sequence)]))
                                            emulator.write(transform_raw(
                                                raw_bytes=device['power']['responses'][_count],
                                                seq_no=pc.sequence))
                                            emulator.flush()
                                        elif device['power']['responses'][_count] is not None:
                                            # we are sending back a device reading
                                            power_status = [ord(x) for x in str(device['power']['responses'][_count])]
                                            pr = PowerControlResponse(data=power_status, sequence=sequence)
                                            logger.debug('>>Power: ' + str([hex(x) for x in pr.serialize()]))
                                            emulator.write(pr.serialize())
                                            emulator.flush()
                                        else:
                                            # otherwise, we do not send a response
                                            pass
                                        # now increment index into our responses, and wrap it if
                                        # we are repeatable
                                        _count += 1
                                        if device['power']['repeatable']:
                                            _count %= len(device['power']['responses'])
                                        device['power']['_count'] = _count
                                        pass
        elif cmd == 'A':
            # ======================> ASSET INFO <======================
            # the second character of packet.data is the actual command/action
            ac = AssetInfoCommand(data_bytes=packet.serialize())

            # return asset info
            for board in configuration['boards']:
                if board_ids_match(board, ac):
                    for device in board['devices']:
                        if device_ids_match(device, ac) and (
                                device['device_type'] == get_device_type_name(ac.device_type) and (
                                'asset_info' in device)):
                            if is_retry and ('retry_responses' in device['asset_info']):
                                # now we can craft a response
                                responses_length = len(device['asset_info']['retry_responses'])
                                # get the responses counter
                                _retry_count = device['asset_info']['_retry_count'] if '_retry_count' in device[
                                    'asset_info'] else 0

                                if responses_length > 0 and _retry_count < responses_length:
                                    if isinstance(device['asset_info']['retry_responses'][_retry_count], list):
                                        # we are sending raw bytes
                                        logger.debug('>>Asset Info: ' + str([hex(x) for x in transform_raw(
                                            raw_bytes=device['asset_info']['retry_responses'][_retry_count],
                                            seq_no=sequence)]))
                                        emulator.write(transform_raw(
                                            raw_bytes=device['asset_info']['retry_responses'][_retry_count],
                                            seq_no=sequence))
                                        emulator.flush()
                                    else:
                                        # otherwise, we do not send a response
                                        pass
                                    # now increment index into our responses, and wrap it if
                                    # we are repeatable
                                    _retry_count += 1
                                    _retry_count %= len(device['asset_info']['retry_responses'])
                                    device['asset_info']['_retry_count'] = _retry_count
                                    pass
                            else:
                                responses_length = len(device['asset_info']['responses'])
                                # get the responses counter
                                _count = device['asset_info']['_count'] if '_count' in device['asset_info'] else 0

                                if responses_length > 0 and _count < responses_length:
                                    if isinstance(device['asset_info']['responses'][_count], list):
                                        # we are sending raw bytes
                                        logger.debug('>>Asset Info: ' + str([hex(x) for x in transform_raw(
                                            raw_bytes=device['asset_info']['responses'][_count],
                                            seq_no=ac.sequence)]))
                                        emulator.write(transform_raw(
                                            raw_bytes=device['asset_info']['responses'][_count],
                                            seq_no=ac.sequence))
                                        emulator.flush()
                                    elif device['asset_info']['responses'][_count] is not None:
                                        # we are sending back asset info
                                        asset_info = [ord(x) for x in str(device['asset_info']['responses'][_count])]
                                        air = AssetInfoResponse(data=asset_info, sequence=sequence)
                                        logger.debug('>>Asset Info: ' + str([hex(x) for x in air.serialize()]))
                                        emulator.write(air.serialize())
                                        emulator.flush()
                                    else:
                                        # otherwise, we do not send a response
                                        pass
                                    # now increment index into our responses, and wrap it if
                                    # we are repeatable
                                    _count += 1
                                    if device['asset_info']['repeatable']:
                                        _count %= len(device['asset_info']['responses'])
                                    device['asset_info']['_count'] = _count
                                    pass
        elif cmd == 'B':
            # ======================> BOOT TARGET <======================
            # the second character of packet.data is the actual command/action
            pc = BootTargetCommand(data_bytes=packet.serialize())

            # return boot target regardless of command - users of the emulator
            # should design the tests to match the anticipated sequence
            # of commands/requests
            for board in configuration['boards']:
                if board_ids_match(board, pc):
                    for device in board['devices']:
                        if device_ids_match(device, pc) and (
                                device['device_type'] == get_device_type_name(pc.device_type) and (
                                'boot_target' in device)):
                            if is_retry and ('retry_responses' in device['boot_target']):
                                # now we can craft a response
                                responses_length = len(device['boot_target']['retry_responses'])
                                # get the responses counter
                                _retry_count = device['boot_target']['_retry_count'] if '_retry_count' in device[
                                    'boot_target'] else 0

                                if responses_length > 0 and _retry_count < responses_length:
                                    if isinstance(device['boot_target']['retry_responses'][_retry_count], list):
                                        # we are sending raw bytes
                                        logger.debug('>>Boot Target: ' + str([hex(x) for x in transform_raw(
                                            raw_bytes=device['boot_target']['retry_responses'][_retry_count],
                                            seq_no=sequence)]))
                                        emulator.write(transform_raw(
                                            raw_bytes=device['boot_target']['retry_responses'][_retry_count],
                                            seq_no=sequence))
                                        emulator.flush()
                                    else:
                                        # otherwise, we do not send a response
                                        pass
                                    # now increment index into our responses, and wrap it if
                                    # we are repeatable
                                    _retry_count += 1
                                    _retry_count %= len(device['boot_target']['retry_responses'])
                                    device['boot_target']['_retry_count'] = _retry_count
                                    pass
                            else:
                                if 'has_state' in device and device['has_state']:
                                    device['_state'] = device['_state'] if '_state' in device else \
                                        device['boot_target']

                                    # toggle device state based on incoming command
                                    # if a ? command, don't do anything, just return existing state
                                    if chr(int(pc.data[1])) == '0':
                                        device['_state'] = device['hdd']
                                    elif chr(int(pc.data[1])) == '1':
                                        device['_state'] = device['pxe']
                                    elif chr(int(pc.data[1])) == '2':
                                        device['_state'] = device['no_override']

                                    boot_target = [ord(x) for x in str(device['_state'])]
                                    btr = BootTargetResponse(data=boot_target, sequence=sequence)
                                    logger.debug('>>Boot Target: ' + str([hex(x) for x in btr.serialize()]))
                                    emulator.write(btr.serialize())
                                    emulator.flush()
                                    pass
                                else:
                                    responses_length = len(device['boot_target']['responses'])
                                    # get the responses counter
                                    _count = device['boot_target']['_count'] if '_count' in device['boot_target'] else 0

                                    if responses_length > 0 and _count < responses_length:
                                        if isinstance(device['boot_target']['responses'][_count], list):
                                            # we are sending raw bytes
                                            logger.debug('>>Boot Target: ' + str([hex(x) for x in transform_raw(
                                                raw_bytes=device['boot_target']['responses'][_count],
                                                seq_no=pc.sequence)]))
                                            emulator.write(transform_raw(
                                                raw_bytes=device['boot_target']['responses'][_count],
                                                seq_no=pc.sequence))
                                            emulator.flush()
                                        elif device['boot_target']['responses'][_count] is not None:
                                            # we are sending back a boot target
                                            boot_target = [ord(x) for x in str(
                                                device['boot_target']['responses'][_count])]
                                            btr = BootTargetResponse(data=boot_target, sequence=sequence)
                                            logger.debug('>>Boot Target: ' + str([hex(x) for x in btr.serialize()]))
                                            emulator.write(btr.serialize())
                                            emulator.flush()
                                        else:
                                            # otherwise, we do not send a response
                                            pass
                                        # now increment index into our responses, and wrap it if
                                        # we are repeatable
                                        _count += 1
                                        if device['boot_target']['repeatable']:
                                            _count %= len(device['boot_target']['responses'])
                                        device['boot_target']['_count'] = _count
                                        pass
        elif cmd == 'W':
            # ======================> WRITE <======================
            # first, determine what kind of a read we are dealing with
            wc = DeviceWriteCommand(data_bytes=packet.serialize())
            for board in configuration['boards']:
                if board_ids_match(board, wc):
                    for device in board['devices']:
                        if device_ids_match(device, wc) and device_types_compatible(device, wc) and ('write' in device):
                            if is_retry and ('retry_responses' in device['write']):
                                # now we can craft a response
                                responses_length = len(device['write']['retry_responses'])
                                # get the responses counter
                                _retry_count = device['write']['_retry_count'] if '_retry_count' in \
                                                                                  device['write'] else 0

                                if responses_length > 0 and _retry_count < responses_length:
                                    if isinstance(device['write']['retry_responses'][_retry_count], list):
                                        # we are sending raw bytes
                                        logger.debug('>>Write: ' + str([hex(x) for x in transform_raw(
                                            raw_bytes=device['write']['retry_responses'][_retry_count],
                                            seq_no=sequence)]))
                                        emulator.write(transform_raw(
                                            raw_bytes=device['write']['retry_responses'][_retry_count],
                                            seq_no=sequence))
                                        emulator.flush()
                                    else:
                                        # otherwise, we do not send a response
                                        pass
                                    # now increment index into our responses, and wrap it if
                                    # we are repeatable
                                    _retry_count += 1
                                    _retry_count %= len(device['write']['retry_responses'])
                                    device['write']['_retry_count'] = _retry_count
                                    pass
                            else:
                                if 'has_state' in device and device['has_state']:
                                    device['_state'] = device['_state'] if '_state' in device else \
                                        device['write']
                                    if device['device_type'] == 'vapor_fan' or device['device_type'] == 'fan_speed':
                                        # ignore fan motor pole setting
                                        device['_state'] = ''.join([chr(x) for x in wc.data[2:]])
                                    else:
                                        device['_state'] = ''.join([chr(x) for x in wc.data[1:]])
                                    logger.debug(device['_state'])

                                    # always return ok for writes
                                    reading = [ord(x) for x in 'W1']
                                    wr = DeviceWriteResponse(device_response=reading, sequence=sequence)
                                    logger.debug('>>Write: ' + str([hex(x) for x in wr.serialize()]))
                                    emulator.write(wr.serialize())
                                    emulator.flush()
                                    pass
                                else:
                                    responses_length = len(device['write']['responses'])
                                    # get the responses counter
                                    _count = device['write']['_count'] if '_count' in device['write'] else 0

                                    if responses_length > 0 and _count < responses_length:
                                        if isinstance(device['write']['responses'][_count], list):
                                            # we are sending raw bytes
                                            logger.debug('>>Write: ' + str([hex(x) for x in transform_raw(
                                                raw_bytes=device['write']['responses'][_count],
                                                seq_no=pc.sequence)]))
                                            emulator.write(transform_raw(
                                                raw_bytes=device['write']['responses'][_count],
                                                seq_no=pc.sequence))
                                            emulator.flush()
                                        elif device['write']['responses'][_count] is not None:
                                            # we are sending back a device reading
                                            write_response = [ord(x) for x in str(device['write']['responses'][_count])]
                                            wr = DeviceWriteResponse(device_response=write_response,
                                                                     sequence=sequence)
                                            logger.debug('>>Write: ' + str([hex(x) for x in wr.serialize()]))
                                            emulator.write(wr.serialize())
                                            emulator.flush()
                                        else:
                                            # otherwise, we do not send a response
                                            pass
                                        # now increment index into our responses, and wrap it if
                                        # we are repeatable
                                        _count += 1
                                        if device['write']['repeatable']:
                                            _count %= len(device['write']['responses'])
                                        device['write']['_count'] = _count
                                        pass
        elif cmd == 'L':
            # ======================> CHAMBER LED <======================
            logger.warning('Chamber LED Command Detected')
            lc = ChamberLedControlCommand(data_bytes=packet.serialize())
            logger.warning('command: {}'.format(lc))

            for board in configuration['boards']:
                if board_ids_match(board, lc):
                    logger.warning('-- board ids match')
                    for device in board['devices']:
                        if device_ids_match(device, lc) and (
                                device['device_type'] == get_device_type_name(lc.device_type) and (
                                'write' in device)):
                            logger.warning('-- devices match')
                            if is_retry and ('retry_responses' in device['write']):
                                # now we can craft a response
                                responses_length = len(device['write']['retry_responses'])
                                # get the responses counter
                                _retry_count = device['write']['_retry_count'] if '_retry_count' in \
                                                                                  device['write'] else 0

                                if responses_length > 0 and _retry_count < responses_length:
                                    if isinstance(device['write']['retry_responses'][_retry_count], list):
                                        # we are sending raw bytes
                                        logger.debug('>>Chamber_LED: ' + str([hex(x) for x in transform_raw(
                                            raw_bytes=device['write']['retry_responses'][_retry_count],
                                            seq_no=sequence)]))
                                        emulator.write(transform_raw(
                                            raw_bytes=device['write']['retry_responses'][_retry_count],
                                            seq_no=sequence))
                                        emulator.flush()
                                    else:
                                        # otherwise, we do not send a response
                                        pass
                                    # now increment index into our responses, and wrap it if
                                    # we are repeatable
                                    _retry_count += 1
                                    _retry_count %= len(device['write']['retry_responses'])
                                    device['write']['_retry_count'] = _retry_count
                                    pass
                            else:
                                if 'has_state' in device and device['has_state']:
                                    # convert incoming command to str for easy parsing, omitting the L at cmd start
                                    cmd_in = ''.join([chr(x) for x in lc.data[1:]])
                                    logger.debug('state {}'.format(cmd_in))

                                    # parse incoming command - format: state, rack, color, blink_state
                                    cmd = cmd_in.split(',')
                                    state = cmd[0]
                                    rack = cmd[1]
                                    color = cmd[2]
                                    blink_state = cmd[3]

                                    # lazy-initialize for each rack encountered - if doesn't exist, then default to
                                    # the value stored in the 'write' field (the rack field is ignored on return)
                                    device['_state'] = device['_state'] if '_state' in device else dict()
                                    device['_state'][rack] = device['_state'][rack] if rack in device['_state'] \
                                        else device['write']

                                    # toggle device state based on incoming blink state
                                    # if a -1 command, don't do anything, just return existing state
                                    if blink_state != '-1':
                                        device['_state'][rack] = state + ',' + color + ',' + blink_state

                                    write_response = [ord(x) for x in str(device['_state'][rack])]
                                    clr = ChamberLedControlResponse(data=write_response, sequence=sequence)
                                    logger.debug('>>Chamber LED: ' + str([hex(x) for x in clr.serialize()]))
                                    emulator.write(clr.serialize())
                                    emulator.flush()
                                    pass
                                else:
                                    responses_length = len(device['write']['responses'])
                                    # get the responses counter
                                    _count = device['write']['_count'] if '_count' in device['write'] else 0

                                    if responses_length > 0 and _count < responses_length:
                                        if isinstance(device['write']['responses'][_count], list):
                                            # we are sending raw bytes
                                            logger.debug('>>Chamber_LED: ' + str([hex(x) for x in transform_raw(
                                                raw_bytes=device['write']['responses'][_count],
                                                seq_no=lc.sequence)]))
                                            emulator.write(transform_raw(
                                                raw_bytes=device['write']['responses'][_count],
                                                seq_no=lc.sequence))
                                            emulator.flush()
                                        elif device['write']['responses'][_count] is not None:
                                            # we are sending back a device reading
                                            write_response = [ord(x) for x in str(device['write']['responses'][_count])]
                                            lr = ChamberLedControlResponse(data=write_response,
                                                                           sequence=sequence)
                                            logger.debug('>>Chamber_LED: ' + str([hex(x) for x in lr.serialize()]))
                                            emulator.write(lr.serialize())
                                            emulator.flush()
                                        else:
                                            # otherwise, we do not send a response
                                            pass
                                        # now increment index into our responses, and wrap it if
                                        # we are repeatable
                                        _count += 1
                                        if device['write']['repeatable']:
                                            _count %= len(device['write']['responses'])
                                        device['write']['_count'] = _count
                                        pass
        elif cmd == 'H':
            # ======================> HOST INFO (NOT ACTUAL PLC) <======================
            lc = ChamberLedControlCommand(data_bytes=packet.serialize())

            for board in configuration['boards']:
                if board_ids_match(board, lc):
                    for device in board['devices']:
                        if device_ids_match(device, lc) and (
                                device['device_type'] == get_device_type_name(lc.device_type) and (
                                'host_info' in device)):
                            if is_retry and ('retry_responses' in device['host_info']):
                                # now we can craft a response
                                responses_length = len(device['host_info']['retry_responses'])
                                # get the responses counter
                                _retry_count = device['host_info']['_retry_count'] if '_retry_count' in \
                                                                                      device['host_info'] else 0

                                if responses_length > 0 and _retry_count < responses_length:
                                    if isinstance(device['host_info']['retry_responses'][_retry_count], list):
                                        # we are sending raw bytes
                                        logger.debug('>>Host_Info: ' + str([hex(x) for x in transform_raw(
                                            raw_bytes=device['host_info']['retry_responses'][_retry_count],
                                            seq_no=sequence)]))
                                        emulator.write(transform_raw(
                                            raw_bytes=device['host_info']['retry_responses'][_retry_count],
                                            seq_no=sequence))
                                        emulator.flush()
                                    else:
                                        # otherwise, we do not send a response
                                        pass
                                    # now increment index into our responses, and wrap it if
                                    # we are repeatable
                                    _retry_count += 1
                                    _retry_count %= len(device['host_info']['retry_responses'])
                                    device['host_info']['_retry_count'] = _retry_count
                                    pass
                            else:
                                responses_length = len(device['host_info']['responses'])
                                # get the responses counter
                                _count = device['host_info']['_count'] if '_count' in device['host_info'] else 0

                                if responses_length > 0 and _count < responses_length:
                                    if isinstance(device['host_info']['responses'][_count], list):
                                        # we are sending raw bytes
                                        logger.debug('>>Host_Info: ' + str([hex(x) for x in transform_raw(
                                            raw_bytes=device['host_info']['responses'][_count],
                                            seq_no=lc.sequence)]))
                                        emulator.write(transform_raw(
                                            raw_bytes=device['host_info']['responses'][_count],
                                            seq_no=lc.sequence))
                                        emulator.flush()
                                    elif device['host_info']['responses'][_count] is not None:
                                        # we are sending back a device reading
                                        write_response = [ord(x) for x in str(device['host_info']['responses'][_count])]
                                        lr = HostInfoResponse(data=write_response, sequence=sequence)
                                        logger.debug('>>Host_Info: ' + str([hex(x) for x in lr.serialize()]))
                                        emulator.write(lr.serialize())
                                        emulator.flush()
                                    else:
                                        # otherwise, we do not send a response
                                        pass
                                    # now increment index into our responses, and wrap it if
                                    # we are repeatable
                                    _count += 1
                                    if device['host_info']['repeatable']:
                                        _count %= len(device['host_info']['responses'])
                                    device['host_info']['_count'] = _count
                                    pass
        else:
            # ======================> UNKNOWN <======================
            logger.debug('Unknown command encountered (%s)', cmd)
            pass

        # cache the previous packet, and reset retry flag
        prev_packet = packet
        is_retry = False


if __name__ == '__main__':

    vapor_logging.setup_logging(default_path='/synse/configs/logging/emulator.json')
    logger.info('========================================')
    logger.info('Starting DeviceBus Emulator.')

    # The emulator config file is the one and only param passed to the emulator.
    emulator_config_file = sys.argv[1]
    logger.info('emulator_config_file {}'.format(emulator_config_file))
    with open(emulator_config_file, 'r') as config_file:
        emulator_config = json.load(config_file)

    emulatorDevice = emulator_config['serial_device']

    configFile = emulator_config['emulator_data']
    emulator_data = open(configFile, 'r')
    data = emulator_data.read()
    configuration = json.loads(data)

    while True:
        try:
            main(emulatorDevice)
        except Exception as e:
            logger.exception('Exception encountered processing packet. (%s)', e)
