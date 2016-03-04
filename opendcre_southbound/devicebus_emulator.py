#!/usr/bin/env python
"""
   OpenDCRE Device Bus Test Emulator
   Author:  andrew
   Date:    4/16/2015
   Updated: 6/11/2015 - Add power control/status commands (andrew)
   Updated: 12/4/2015 - Add retry logic support (andrew)

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
import sys
import logging
import vapor_common.vapor_logging as vapor_logging
import json

import devicebus
from definitions import SCAN_ALL_BIT, SAVE_BIT, SHUFFLE_BIT

logger = logging.getLogger()

TERMINATE = False  # set to true to shut down the emulator
configuration = {}  # where our emulator configuration will live

SEQUENCE_NUMBER_SENTINEL = 999      # when encountered, replace with the desired sequence number
CHECKSUM_SENTINEL = 1000            # mask for checksum, remainder is offset of starting byte of checksum

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

    IMPORTANT ADDENDUM 1/18/2016:  The emulator also may be used with PLC comms,
        (without socat).  To run the emulator, run start_opendcre_emulator.sh
        with the parameters to the TTY, configuration file (e.g. simple.json),
        and hardware type (in that case, 0 or PLC_RPI_V1).

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

    Returns: True if they match, False otherwise.

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

    Returns: True if they match, False otherwise.

    """
    return int(config_device['device_id'], 16) == dev_bus_cmd.device_id


# ==============================================================================#
#                                Emulator Main                                  #
# ==============================================================================#

def generate_emulator_checksum(raw_bytes, start, end):
    """ Convenience method for generating a checksum over a raw byte range.
    Redundant to what is in devicebus, but added in this form for simplicity.

    Args:
        raw_bytes: The byte buffer to compute checksum for.
        start: The starting index of the buffer.
        end: The ending index of the buffer to checksum.

    Returns: The checksum over the specified buffer range.

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
        raw_bytes: The raw byte stream from the emulator config.
        seq_no: The sequence number to drop in.

    Returns: A transformed list of bytes based on the input.

    """
    # copy bytes so we do not stomp the emulator config for later uses of the
    # same bytes (otherwise, on the first use, the sentinels are removed for the lifetime of the emulator)
    new_bytes = list(raw_bytes)
    for i, x in enumerate(new_bytes):
        if x == SEQUENCE_NUMBER_SENTINEL:
            new_bytes[i] = seq_no
        elif CHECKSUM_SENTINEL <= x <= CHECKSUM_SENTINEL+255:
            new_bytes[i] = generate_emulator_checksum(new_bytes, x-CHECKSUM_SENTINEL, i)
    return new_bytes


def inject_error(raw_bytes):
    """ Inject an error in a serialized devicebus packet by messing up the data within by adding 1 to each byte.
    The header and trailer are not affected, but the bytes within the packet are.

    Args:
        raw_bytes: The raw bytes to inject an error into.

    Returns: A transformed list of raw bytes with erroneous data within.

    """
    for i in range(len(raw_bytes)):
        if raw_bytes[i] != devicebus.PKT_VALID_HEADER and raw_bytes[i] != devicebus.PKT_VALID_TRAILER:
            raw_bytes[i] = (raw_bytes[i] + 1) % 255
    return raw_bytes


def main(emulator_device):
    """ The main emulator control loop. Runs until it is time to stop.

    Args:
        emulator_device: The serial port device name (e.g. /dev/ttyVapor002 or /dev/ttyAMA0) to listen on.

    Returns: None.

    """
    emulator = devicebus.DeviceBus(hardware_type=devicebus.DEVICEBUS_EMULATOR_V1,
                                   device_name=emulator_device, timeout=None)
    prev_packet = None
    is_retry = False

    while not TERMINATE:
        # retrieve packet from client
        try:
            packet = devicebus.DeviceBusPacket(serial_reader=emulator)
            sequence = packet.sequence  # to be plumbed into all non-static packets sent back
            logger.debug("<<Packet " + str([hex(x) for x in packet.serialize()]))
        except Exception as ex:
            logger.error("Exception encountered deserializing packet (%s).", ex)
            return

        # grab command from packet data
        cmd = chr(packet.data[0])

        # check for retry request first
        if cmd == '?':
            packet = prev_packet  # determine what is being retried
            is_retry = True  # set to indicate should retry request
            cmd = chr(packet.data[0])  # get the command out of the prev req
            logger.debug("Retry Encountered - Command (%s)", cmd)

        # handle command from packet
        if cmd == 'D':
            # ======================> SCAN <======================
            sc = devicebus.DumpCommand(data_bytes=packet.serialize())
            # if the save bit is enabled in the board_id, do nothing, since we
            # expect no response back in this case.
            if (sc.board_id >> SAVE_BIT) & 0x01 == 1:
                logger.debug("Encountered Save Bit")
            else:
                # match sc.board_id against a board_id in configuration - if
                # the board_id does not exist, send nothing; if board_id is 0xFF
                # return all boards unless we are emulating early firmware not
                # supporting scan-all-boards, where we instead return nothing
                if (sc.board_id >> SCAN_ALL_BIT) & 0x01 != 1:
                    for board in configuration["boards"]:
                        if board_ids_match(board, sc):
                            if is_retry:
                                if "retry_raw_data" in board:
                                    # now we can craft a response
                                    responses_length = len(board["retry_raw_data"])
                                    # get the responses counter
                                    _retry_count = board["_retry_scan_count"] if "_retry_scan_count" in board else 0

                                    if responses_length > 0 and _retry_count < responses_length:
                                        if isinstance(board["retry_raw_data"][_retry_count], list):
                                            # we are sending raw bytes
                                            logger.debug(">>Scan: " + str([hex(x) for x in transform_raw(
                                                    raw_bytes=board['retry_raw_data'][_retry_count], seq_no=sequence)]))
                                            emulator.write(transform_raw(board["retry_raw_data"][_retry_count],
                                                                         seq_no=sequence))
                                            emulator.flush()
                                        else:
                                            # otherwise, we do not send a response
                                            pass
                                        # now increment index into our responses, and wrap it if
                                        # we are repeatable
                                        _retry_count += 1
                                        _retry_count %= len(board["retry_raw_data"])
                                        board["_retry_scan_count"] = _retry_count
                                        pass
                            else:
                                if "raw_data" in board:
                                    # now we can craft a response
                                    responses_length = len(board["raw_data"])
                                    # get the responses counter
                                    _scan_count = board["_scan_count"] if "_scan_count" in board else 0

                                    if responses_length > 0 and _scan_count < responses_length:
                                        if isinstance(board["raw_data"][_scan_count], list):
                                            for packet in board["raw_data"][_scan_count]:
                                                # we are sending raw bytes
                                                logger.debug(">>Scan: " + str([hex(x) for x in
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
                                        _scan_count %= len(board["raw_data"])
                                        board["_scan_count"] = _scan_count
                                        pass
                                else:
                                    for device in board["devices"]:
                                        srp = devicebus.DumpResponse(
                                                board_id=board["board_id"],
                                                sequence=sequence,
                                                device_id=device["device_id"],
                                                device_type=devicebus.get_device_type_code(device["device_type"]),
                                                data=[devicebus.get_device_type_code(device["device_type"])]
                                        )
                                        logger.debug(">>Scan: " + str([hex(x) for x in srp.serialize()]))
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
                        logger.debug("SCANALL COUNT : {}".format(_scanall_count))
                        if (sc.board_id >> SHUFFLE_BIT) & 0x01 == 0:
                            # this is an initial attempt
                            if configuration['scanall'][_scanall_count]['initial']['result'] == 'error':
                                failed_board = configuration['scanall'][_scanall_count]['initial']['failed_board']
                                logger.debug(">> Scanall: Returning results with bad board {}.".format(failed_board))
                            # otherwise, return everything as specified in the config
                            else:
                                logger.debug(">> Scanall: Returning all results without error.")
                                # advance to the next scan test
                                _scanall_count += 1
                                _scanall_count %= len(configuration['scanall'])
                                configuration['_scanall_count'] = _scanall_count
                                logger.debug("SCANALL COUNT INCREMENTED : {}".format(_scanall_count))
                            pass
                        else:
                            # this is a shuffle attempt
                            _scanall_retry_count = \
                                configuration['scanall'][_scanall_count]['_scanall_retry_count'] \
                                if '_scanall_retry_count' in configuration['scanall'][_scanall_count] else 0
                            logger.debug("SCANALL RETRY COUNT {}".format(_scanall_retry_count))
                            if configuration['scanall'][_scanall_count]['retry'][_scanall_retry_count]['result'] == 'error':
                                failed_board = \
                                    configuration['scanall'][_scanall_count]['retry'][_scanall_retry_count]['failed_board']
                                logger.debug(">> Scanall retry: Returning results with bad board {}.".format(failed_board))
                            else:
                                # otherwise, return everything as specified in the config
                                logger.debug(">> Scanall retry: Returning all results without error.")
                            _scanall_retry_count += 1
                            logger.debug("SCANALL RETRY COUNT INCREMENTED : {}".format(_scanall_retry_count))
                            configuration['scanall'][_scanall_count]['_scanall_retry_count'] = _scanall_retry_count
                            if _scanall_retry_count == len(configuration['scanall'][_scanall_count]['retry']):
                                # advance to the next scan test
                                _scanall_count += 1
                                _scanall_count %= len(configuration['scanall'])
                                configuration['_scanall_count'] = _scanall_count
                                logger.debug("RESETTING SCANALL COUNT {}".format(_scanall_count))

                    # at this point, if failed_board is not None, we need to muck up the results from failed_board -
                    # all other results will return fine
                    for board in configuration["boards"]:
                        if is_retry:
                            if "retry_raw_data" in board:
                                rsp_bytes = transform_raw(raw_bytes=board['retry_raw_data'], seq_no=sequence)
                                if board['board_id'] == failed_board:
                                    rsp_bytes = inject_error(rsp_bytes)
                                logger.debug(">>Scan: " + str([hex(x) for x in rsp_bytes]))
                                emulator.write(rsp_bytes)
                                emulator.flush()
                        else:
                            if "raw_data" in board:
                                # now we can craft a response
                                responses_length = len(board["raw_data"])
                                # get the responses counter
                                _scan_count = board["_scan_count"] if "_scan_count" in board else 0

                                if responses_length > 0 and _scan_count < responses_length:
                                    if isinstance(board["raw_data"][_scan_count], list):
                                        for packet in board["raw_data"][_scan_count]:
                                            # we are sending raw bytes
                                            rsp_bytes = transform_raw(raw_bytes=packet, seq_no=sequence)
                                            if board['board_id'] == failed_board:
                                                rsp_bytes = inject_error(rsp_bytes)
                                            logger.debug(">>Scan: " + str([hex(x) for x in rsp_bytes]))
                                            emulator.write(rsp_bytes)
                                            emulator.flush()
                                    else:
                                        # otherwise, we do not send a response
                                        pass
                                    # now increment index into our responses, and wrap it if
                                    # we are repeatable
                                    _scan_count += 1
                                    _scan_count %= len(board["raw_data"])
                                    board["_scan_count"] = _scan_count
                                    pass
                            else:
                                for device in board["devices"]:
                                    srp = devicebus.DumpResponse(
                                            board_id=board["board_id"],
                                            sequence=sequence,
                                            device_id=device["device_id"],
                                            device_type=devicebus.get_device_type_code(device["device_type"]),
                                            data=[devicebus.get_device_type_code(device["device_type"])]
                                    )
                                    rsp_bytes = srp.serialize()
                                    if board['board_id'] == failed_board:
                                        logger.debug("Injecting bad bytes to response.")
                                        rsp_bytes = inject_error(rsp_bytes)
                                    logger.debug(">>Scan: " + str([hex(x) for x in rsp_bytes]))
                                    emulator.write(rsp_bytes)
                                    emulator.flush()
                # if we get here, nothing to send
                pass

        elif cmd == 'V':
            # ======================> VERSION <======================
            # TODO: support a collection of versions in the schema
            vc = devicebus.VersionCommand(data_bytes=packet.serialize())
            for board in configuration["boards"]:
                if board_ids_match(board, vc):
                    if is_retry:
                        if "retry_firmware_version" in board:
                            # now we can craft a response
                            responses_length = len(board["retry_firmware_version"])
                            # get the responses counter
                            _retry_count = board["_retry_version_count"] if "_retry_version_count" in board else 0

                            if responses_length > 0 and _retry_count < responses_length:
                                if isinstance(board["retry_firmware_version"][_retry_count], list):
                                    # we are sending raw bytes
                                    logger.debug(">>Version: " + str([hex(x) for x in
                                                                      transform_raw(raw_bytes=board['retry_firmware_version'][_retry_count],
                                                                      seq_no=sequence)]))
                                    emulator.write(
                                            transform_raw(raw_bytes=board["retry_firmware_version"][_retry_count],
                                                          seq_no=sequence))
                                    emulator.flush()
                                else:
                                    # otherwise, we do not send a response
                                    pass
                                # now increment index into our responses, and wrap it if
                                # we are repeatable
                                _retry_count += 1
                                _retry_count %= len(board["retry_firmware_version"])
                                board["_retry_version_count"] = _retry_count
                                pass
                    else:
                        if isinstance(board["firmware_version"], list):
                            # sending raw bytes
                            logger.debug(">>Version: " + str([hex(x) for x in
                                                              transform_raw(raw_bytes=board['firmware_version'],
                                                                            seq_no=sequence)]))
                            emulator.write(transform_raw(raw_bytes=board["firmware_version"], seq_no=sequence))
                            emulator.flush()
                        else:
                            vr = devicebus.VersionResponse(
                                    sequence=sequence,
                                    version_string=board["firmware_version"]
                            )  # TODO: set board_id field?
                            logger.debug(">>Version: " + str([hex(x) for x in vr.serialize()]))
                            emulator.write(vr.serialize())
                            emulator.flush()
                            # otherwise, no response

        elif cmd == 'R':
            # ======================> READ <======================
            # first, determine what kind of a read we are dealing with
            if len(packet.data) == 1:
                # data -> ["R"] : Read Command
                rc = devicebus.DeviceReadCommand(data_bytes=packet.serialize())
                for board in configuration["boards"]:
                    if board_ids_match(board, rc):
                        for device in board["devices"]:
                            if device_ids_match(device, rc) and (device["device_type"] ==
                                                                 devicebus.get_device_type_name(rc.device_type) and
                                                                 ("read" in device)):
                                if is_retry and ("retry_responses" in device["read"]):
                                    # now we can craft a response
                                    responses_length = len(device["read"]["retry_responses"])
                                    # get the responses counter
                                    _retry_count = device["read"]["_retry_count"] if "_retry_count" in \
                                                                                     device["read"] else 0

                                    if responses_length > 0 and _retry_count < responses_length:
                                        if isinstance(device["read"]["retry_responses"][_retry_count], list):
                                            # we are sending raw bytes
                                            logger.debug(">>Read: " + str(
                                                    [hex(x) for x in
                                                     transform_raw(raw_bytes=
                                                                   device['read']['retry_responses'][_retry_count],
                                                     seq_no=sequence)]))
                                            emulator.write(
                                                    transform_raw(raw_bytes=
                                                                  device["read"]["retry_responses"][_retry_count],
                                                                  seq_no=sequence))
                                            emulator.flush()
                                        else:
                                            # otherwise, we do not send a response
                                            pass
                                        # now increment index into our responses, and wrap it if
                                        # we are repeatable
                                        _retry_count += 1
                                        _retry_count %= len(device["read"]["retry_responses"])
                                        device["read"]["_retry_count"] = _retry_count
                                        pass
                                else:
                                    # now we can craft a response
                                    responses_length = len(device["read"]["responses"])
                                    # get the responses counter
                                    _count = device["read"]["_count"] if "_count" in device["read"] else 0

                                    if responses_length > 0 and _count < responses_length:
                                        if isinstance(device["read"]["responses"][_count], list):
                                            # we are sending raw bytes
                                            logger.debug(
                                                    ">>Read: " + str(
                                                            [hex(x) for x in
                                                             transform_raw(raw_bytes=
                                                                           device['read']['responses'][_count],
                                                                           seq_no=sequence)]))
                                            emulator.write(
                                                    transform_raw(raw_bytes=device["read"]["responses"][_count],
                                                                  seq_no=sequence))
                                            emulator.flush()
                                        elif device["read"]["responses"][_count] is not None:
                                            # we are sending back a device reading
                                            reading = [ord(x) for x in str(device["read"]["responses"][_count])]
                                            rr = devicebus.DeviceReadResponse(device_reading=reading, sequence=sequence)
                                            logger.debug(">>Read: " + str([hex(x) for x in rr.serialize()]))
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
        elif cmd == 'P':
            # ======================> POWER CONTROL <======================
            # the second character of packet.data is the actual command/action
            pc = devicebus.PowerControlCommand(data_bytes=packet.serialize())

            # return power status regardless of command - users of the emulator
            # should design the config tests to match the anticipated sequence
            # of commands/requests
            for board in configuration["boards"]:
                if board_ids_match(board, pc):
                    for device in board["devices"]:
                        if device_ids_match(device, pc) and (
                                        device["device_type"] == devicebus.get_device_type_name(pc.device_type) and (
                                            "power" in device)):
                            if is_retry and ("retry_responses" in device["power"]):
                                # now we can craft a response
                                responses_length = len(device["power"]["retry_responses"])
                                # get the responses counter
                                _retry_count = device["power"]["_retry_count"] if "_retry_count" in device[
                                    "power"] else 0

                                if responses_length > 0 and _retry_count < responses_length:
                                    if isinstance(device["power"]["retry_responses"][_retry_count], list):
                                        # we are sending raw bytes
                                        logger.debug(">>Power: " + str(
                                                [hex(x) for x in
                                                 transform_raw(raw_bytes=device['power']['retry_responses'][_retry_count],
                                                 seq_no=sequence)]))
                                        emulator.write(
                                                transform_raw(raw_bytes=device["power"]["retry_responses"][_retry_count],
                                                              seq_no=sequence))
                                        emulator.flush()
                                    else:
                                        # otherwise, we do not send a response
                                        pass
                                    # now increment index into our responses, and wrap it if
                                    # we are repeatable
                                    _retry_count += 1
                                    _retry_count %= len(device["power"]["retry_responses"])
                                    device["power"]["_retry_count"] = _retry_count
                                    pass
                            else:
                                responses_length = len(device["power"]["responses"])
                                # get the responses counter
                                _count = device["power"]["_count"] if "_count" in device["power"] else 0

                                if responses_length > 0 and _count < responses_length:
                                    if isinstance(device["power"]["responses"][_count], list):
                                        # we are sending raw bytes
                                        logger.debug(
                                                ">>Power: " + str(
                                                        [hex(x) for x in
                                                         transform_raw(raw_bytes=device['power']['responses'][_count],
                                                         seq_no=pc.sequence)]))
                                        emulator.write(
                                                transform_raw(raw_bytes=device["power"]["responses"][_count],
                                                              seq_no=pc.sequence))
                                        emulator.flush()
                                    elif device["power"]["responses"][_count] is not None:
                                        # we are sending back a device reading
                                        power_status = [ord(x) for x in str(device["power"]["responses"][_count])]
                                        pr = devicebus.PowerControlResponse(data=power_status, sequence=sequence)
                                        logger.debug(">>Power: " + str([hex(x) for x in pr.serialize()]))
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
        elif cmd == 'W':
            # ======================> WRITE <======================
            # first, determine what kind of a read we are dealing with
            wc = devicebus.DeviceWriteCommand(data_bytes=packet.serialize())

            for board in configuration["boards"]:
                if board_ids_match(board, wc):
                    for device in board["devices"]:
                        if device_ids_match(device, wc) and (
                                        device["device_type"] == devicebus.get_device_type_name(wc.device_type) and (
                                            "write" in device)):
                            if is_retry and ("retry_responses" in device["write"]):
                                # now we can craft a response
                                responses_length = len(device["write"]["retry_responses"])
                                # get the responses counter
                                _retry_count = device["write"]["_retry_count"] if "_retry_count" in \
                                                                                  device["write"] else 0

                                if responses_length > 0 and _retry_count < responses_length:
                                    if isinstance(device["write"]["retry_responses"][_retry_count], list):
                                        # we are sending raw bytes
                                        logger.debug(">>Write: " + str(
                                                [hex(x) for x in
                                                 transform_raw(raw_bytes=device['write']['retry_responses'][_retry_count],
                                                 seq_no=sequence)]))
                                        emulator.write(
                                                transform_raw(raw_bytes=device["write"]["retry_responses"][_retry_count],
                                                              seq_no=sequence))
                                        emulator.flush()
                                    else:
                                        # otherwise, we do not send a response
                                        pass
                                    # now increment index into our responses, and wrap it if
                                    # we are repeatable
                                    _retry_count += 1
                                    _retry_count %= len(device["write"]["retry_responses"])
                                    device["write"]["_retry_count"] = _retry_count
                                    pass
                            else:
                                responses_length = len(device["write"]["responses"])
                                # get the responses counter
                                _count = device["write"]["_count"] if "_count" in device["write"] else 0

                                if responses_length > 0 and _count < responses_length:
                                    if isinstance(device["write"]["responses"][_count], list):
                                        # we are sending raw bytes
                                        logger.debug(
                                                ">>Write: " + str(
                                                        [hex(x) for x in
                                                         transform_raw(raw_bytes=device['write']['responses'][_count],
                                                         seq_no=pc.sequence)]))
                                        emulator.write(
                                                transform_raw(raw_bytes=device["write"]["responses"][_count],
                                                              seq_no=pc.sequence))
                                        emulator.flush()
                                    elif device["write"]["responses"][_count] is not None:
                                        # we are sending back a device reading
                                        write_response = [ord(x) for x in str(device["write"]["responses"][_count])]
                                        wr = devicebus.DeviceWriteResponse(device_response=write_response,
                                                                           sequence=sequence)
                                        logger.debug(">>Write: " + str([hex(x) for x in wr.serialize()]))
                                        emulator.write(wr.serialize())
                                        emulator.flush()
                                    else:
                                        # otherwise, we do not send a response
                                        pass
                                    # now increment index into our responses, and wrap it if
                                    # we are repeatable
                                    _count += 1
                                    if device["write"]["repeatable"]:
                                        _count %= len(device["write"]["responses"])
                                    device["write"]["_count"] = _count
                                    pass
        else:
            # ======================> UNKNOWN <======================
            logger.debug("Unknown command encountered (%s)", cmd)
            pass

        # cache the previous packet, and reset retry flag
        prev_packet = packet
        is_retry = False


if __name__ == "__main__":
    # the serial device we will listen on,
    # passed in as first parameter to this program
    emulatorDevice = sys.argv[1]

    hardware = devicebus.DEVICEBUS_EMULATOR_V1
    if len(sys.argv) == 4:
        hardware = int(sys.argv[3])

    vapor_logging.setup_logging(default_path='logging_emulator.json')
    logger.info("========================================")
    logger.info("Starting DeviceBus Emulator.")

    if hardware == devicebus.DEVICEBUS_RPI_HAT_V1:
        import devicebus_interfaces.plc_rpi_v1 as plc_rpi_v1
        for x in range(2):
            config = plc_rpi_v1.OPENDCRE_DEFAULT_CONFIGURATION
            # FIXME: the emulator is a subordinate device on the bus, and needs to handle
            # FIXME: auto_sleep differently than the master, where we instead receive a WUM and need to wake
            # FIXME: ourselves up based on the incoming WUM.  For most testing purposes, this is not terrifically
            # FIXME: useful or necessary, but is something that should be added here when possible.
            config['auto_sleep'] = False
            config['auto_wum'] = False
            plc_rpi_v1.wake()  # just to be on the safe side
            plc_rpi_v1.configure(serial_device=emulatorDevice, configuration=config)

    # the JSON configuration file name is
    # passed in as the second parameter to this program
    configFile = sys.argv[2]
    emulator_data = open(configFile, "r")
    data = emulator_data.read()
    configuration = json.loads(data)

    while True:
        try:
            main(emulatorDevice)
        except Exception as e:
            logger.error("Exception encountered processing packet. (%s)", e)
