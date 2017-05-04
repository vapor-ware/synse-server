#!/usr/bin/env python
""" Synse Device Bus Module

    Author:  andrew, steven
    Date:    4/13/2015
    Update:  6/11/2015 - Add power control, remap from devices to devices. (ABC)

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
import logging
import serial

from synse.errors import *
from synse.constants import *
from synse.utils import (
    board_id_to_bytes,
    device_id_to_bytes,
    board_id_join_bytes,
    device_id_join_bytes,
    get_device_type_code
)

logger = logging.getLogger(__name__)

# ============================================================================== #
#                        Packet Constants Definition                             #
# ============================================================================== #

# minimum length for a packet. determined by adding:
#   - header            (1 byte)
#   - length            (1 byte)
#   - sequence number   (1 byte)
#   - device type       (1 byte)
#   - board number      (4 bytes)
#   - device id         (2 byte)
#   - data              non-constant
#   - checksum          (1 byte)
#   - trailer           (1 byte)
#
PKT_MIN_LENGTH = 12

# the number of bytes composing the meta info for the packet (header byte,
# length byte, trailer byte)
PKT_META_BYTES = 3

# valid header byte for the packet
PKT_VALID_HEADER = 0x01

# valid trailer byte for the packet
PKT_VALID_TRAILER = 0x04

# ============================================================================== #
#                       Begin DeviceBus Definition                               #
# ============================================================================== #


class DeviceBus(object):
    """ DeviceBus is an abstraction layer on top of serial connection that
    mediates access to the device bus based on the hardware profile in use.
    """
    def __init__(self, hardware_type=DEVICEBUS_UNKNOWN_HARDWARE, device_name=None, timeout=0.25, bps=115200):
        """ Create a new instance of the DeviceBus used to communicate with
        devices on the device bus.

        Depending on the hardware_type, different configuration actions may be
        taken. This also sets up the serial_device based on device_name, which
        is used for reads/writes/flushes.

        hardware_type is the type of hardware to initialize the DeviceBus with:
            DEVICEBUS_VEC_V1 : Configure the V1 VEC (Vapor CORE) for PLC.
            DEVICEBUS_EMULATOR_V1 : Configure the serial emulator.

        device_name is the name of the serial device on the local system that
        is used for serial communications (e.g. /dev/ttyAMA0).

        timeout is the time, in seconds, before a read or write operation times
        out on the serial device.
        """
        if device_name is None:
            logger.error('Attempt to initialize DeviceBus with no device_name.')
            raise ValueError('Must specify a valid device_name for serial device.')

        self.hardware_type = hardware_type
        self.serial_device_name = device_name
        self.timeout = timeout
        self.speed_bps = bps

        # first, configure the hardware itself, based on hardware type
        if self.hardware_type == DEVICEBUS_VEC_V1:
            raise NotImplementedError('VEC_V1 is not yet supported.')

        elif self.hardware_type == DEVICEBUS_EMULATOR_V1:
            # no special hardware config needed
            pass

        else:
            msg = 'Invalid hardware_type specified for reading device bus. {}'.format(self.hardware_type)
            logger.error(msg)
            raise ValueError(msg)

        # at this point, the serial connection is ready to go,
        # so set up the serial_device based on device_name
        self.serial_device = serial.Serial(self.serial_device_name, self.speed_bps, timeout=self.timeout)
        self.flush_all()
        logger.debug('Initialized DeviceBus with hardware: %d device_name: %s speed: %d timeout: %d',
                     self.hardware_type, self.serial_device_name, self.speed_bps, self.timeout or 0)

    def flush_all(self):
        """ Flush all input and output from the serial buffers.

        Generally used when starting a new command on the device bus,
        where there may be lingering noise/junk to clear out.
        """
        if self.serial_device is not None:
            self.serial_device.flushInput()
            self.serial_device.flushOutput()

    def flush(self):
        """ Flush output on the DeviceBus via its serial_device.
        """
        if self.serial_device is not None:
            self.serial_device.flush()

    def read(self, length=0):
        """ Read from the DeviceBus the given number of bytes.

        This function wraps all hardware operations to ensure correct platform-
        specific functionality occurs as part of the read operation.

        Args:
            length (int): the number of bytes to read.

        Returns:
            str: the byte data read. If the read times out, no bytes may be returned.
        """
        if self.serial_device is not None:
            # first, take any action to ensure the bus is readable - for
            # example, wake up all devices on the bus prior to doing read
            # NB: wake may not be needed since the bus is already awake on
            #     write...
            if self.hardware_type == DEVICEBUS_VEC_V1:
                # TODO: call plc_vec_v1.read() to ensure awake
                pass
            elif self.hardware_type == DEVICEBUS_EMULATOR_V1:
                # no action needed on emulator - it's awake.
                pass
            else:
                logger.error('Invalid hardware_type for reading device bus. (%d)', self.hardware_type)
                raise ValueError('Invalid hardware_type for reading device bus.')
            return self.serial_device.read(length)

    def write(self, data=None):
        """ Write to the DeviceBus the given bytes.

        This function wraps all hardware operations to ensure correct platform-
        specific functionality occurs as part of the write operation.

        Args:
            data: the bytes to write.

        Returns:
            int: the number of bytes written. A write may time out, in which case
                a SerialTimeoutException is raised.
        """
        if self.serial_device is not None:
            # first, take any action to ensure the bus is writeable - for
            # example, wake up all devices on the bus prior to doing write
            if self.hardware_type == DEVICEBUS_VEC_V1:
                # TODO: call plc_vec_v1.write() to ensure awake
                pass
            elif self.hardware_type == DEVICEBUS_EMULATOR_V1:
                # no action needed on emulator - it's awake.
                pass
            else:
                logger.error('Invalid hardware_type for writing device bus. (%d)', self.hardware_type)
                raise ValueError('Invalid hardware_type for writing to device bus.')
            return self.serial_device.write(data)

# ============================================================================== #
#                    Begin DeviceBusPacket Definition                            #
# ============================================================================== #


class DeviceBusPacket(object):
    """ DeviceBusPacket is a representation of a single packet that travels the
    device bus.
    """
    def __init__(self, serial_reader=None, expected_sequence=None, data_bytes=None, sequence=0x01, device_type=0xFF,
                 board_id=0x00000000, device_id=0xFFFF, data=None):
        """ Construct a new DeviceBusPacket. There are three real ways to do this -
        either via the data_bytes parameter, or via the individual fields of the packet
        itself (in that case, the header, length, checksum and trailer are all
        automatically generated). Data must be a list of data_bytes. The third way is
        to use serial_reader, which will read a generic packet from the serial stream.
        """
        if serial_reader is not None:
            # this routine will read from serial into a buffer as follows:
            # get header and length data_bytes
            serialbytes = []
            try:
                is_valid_sequence = False
                # drop any packets that do not match expected sequence number, unless expected_sequence is None.
                # spurious packets may arrive due to bus devices sending responses on retry after we have given up
                while not is_valid_sequence:
                    # ignore any leading noise that may be present
                    header = ord(serial_reader.read(1))
                    while header != PKT_VALID_HEADER:
                        header = ord(serial_reader.read(1))
                    serialbytes.append(header)
                    serialbytes.append(ord(serial_reader.read(1)))
                    # read length data_bytes
                    for x in serial_reader.read(serialbytes[1]):
                        serialbytes.append(ord(x))
                    # read one byte for trailer
                    serialbytes.append(ord(serial_reader.read(1)))
                    # now make the packet
                    self.deserialize(serialbytes)
                    is_valid_sequence = True if expected_sequence is None else expected_sequence == self.sequence
                    if not is_valid_sequence:
                        logger.debug('Invalid sequence number - expected %d, got %d.', expected_sequence, self.sequence)
            except (BusDataException, ChecksumException) as e:
                # we want to surface these exceptions, since they indicate that
                # invalid/malformed data was read off the bus. these exceptions
                # should trigger a retry mechanism (and thus we want to raise
                # them as-is, instead of collecting them under a general failure
                logger.debug('<<Invalid_data ({}): {}'.format(e.message, str([hex(x) for x in serialbytes])))
                raise e
            except Exception:
                # a catchall exception used to indicate that something bad has
                # happened - this could be related to errors reading off the bus
                # or reading nothing at all. in either case, we are unable to
                # recover, so BusTimeoutException is passed up the chain for
                # appropriate handling.
                raise BusTimeoutException('No response from bus.')

        elif data_bytes is not None:
            # if we have a raw packet to build off of, populate our fields with
            # the deserialized result
            self.deserialize(data_bytes)

        else:
            # otherwise, we populate our fields as provided by the user
            self.sequence = sequence
            self.device_type = device_type
            self.board_id = board_id
            self.device_id = device_id
            if isinstance(data, list):
                self.data = data
            else:
                self.data = [data]

    def serialize(self):
        """ Generate a serialized byte representation of the given packet. All of the
        packet fields must be populated in the DeviceBusPacket instance for the
        serialization to be successful. If any of the fields are missing, serialization
        will fail with a BusDataException.

        Raises:
            BusDataException: if any of the packet fields are missing.
        """
        if self.sequence is None or self.device_type is None or self.board_id is None or self.device_id is None \
                or self.data is None:
            raise BusDataException('All fields of a packet must be specified in order to be serialized.')

        # find length of packet. Sequence, device type, and checksum are always 1 byte;
        # device_id is two bytes and board id is always 4 bytes - add those up to 9
        length = 9 + len(self.data)
        # generate the list of 4 bytes which make up the board_id
        board_id_bytes = board_id_to_bytes(self.board_id)
        # generate the list of 2 bytes which make up the device_id
        device_id_bytes = device_id_to_bytes(self.device_id)
        # generate checksum over packet contents
        checksum = self.generate_checksum(self.sequence, self.device_type, board_id_bytes, device_id_bytes, self.data)
        # construct and return packet
        packet = [PKT_VALID_HEADER, length, self.sequence, self.device_type, board_id_bytes[0], board_id_bytes[1],
                  board_id_bytes[2], board_id_bytes[3], device_id_bytes[0], device_id_bytes[1]]

        # fn refs are re-evaluated each time in the loop, so define it outside the loop
        append = packet.append
        for x in self.data:
            append(x)
        append(checksum)
        append(PKT_VALID_TRAILER)
        return packet

    def deserialize(self, packet_bytes):
        """ Populate the fields of a DeviceBusPacket instance.

        :param packet_bytes: - They bytes to use to populate the packet instance.

        Raises:
            BusDataException: if the packet is smaller than the minimum packet
                size, if the packet has an invalid header byte, if the packet
                has an invalid trailer byte, or if the length byte in the packet
                does not match the actual length of the packet.
            ChecksumException: if checksum validation fails on the packet being
                deserialized.
        """
        # check length to make sure we have at minimum the min packet length
        if len(packet_bytes) < PKT_MIN_LENGTH:
            raise BusDataException('Invalid packet byte stream length of ' + str(len(packet_bytes)))

        # check header byte - if invalid, toss
        if packet_bytes[0] != PKT_VALID_HEADER:
            raise BusDataException('No header byte found in incoming packet.')

        # check length - if packet_bytes len doesn't match, toss
        if packet_bytes[1] != len(packet_bytes) - PKT_META_BYTES:
            raise BusDataException('Invalid length from incoming packet ({}).'.format(packet_bytes[1]))

        # get sequence num
        self.sequence = packet_bytes[2]

        # get device type
        self.device_type = packet_bytes[3]

        # get board id
        self.board_id = board_id_join_bytes(packet_bytes[4:8])

        # get device id
        self.device_id = device_id_join_bytes(packet_bytes[8:10])

        # get data (up to 32 bytes) - todo multi-packet transmissions
        self.data = [x for x in packet_bytes[10:len(packet_bytes) - 2]]

        # get the checksum and verify it - toss if no good
        check = self.generate_checksum(self.sequence, self.device_type, self.board_id, self.device_id, self.data)
        if check != packet_bytes[len(packet_bytes) - 2]:
            raise ChecksumException('Invalid checksum in incoming packet.')

        # get the trailer byte - toss if no good
        if packet_bytes[len(packet_bytes) - 1] != PKT_VALID_TRAILER:
            raise BusDataException('Invalid trailer byte found in incoming packet.')
        # if we make it here, the packet successfully was deserialized!

    @staticmethod
    def generate_checksum(sequence, device_type, board_id, device_id, data):
        """ Generate and return packet checksum given its fields. Twos complement
        of 0xFF & the sum of bytes from devicetype to data end.

        Args:
            sequence: the sequence number.
            device_type: the device type.
            board_id: the board id.
            device_id: the device id.
            data: the data bytes.

        Returns: The packet checksum
        """
        board_id_bytes = board_id_to_bytes(board_id)
        device_id_bytes = device_id_to_bytes(device_id)

        checksum = sequence + device_type + sum(board_id_bytes) + sum(device_id_bytes)
        for x in data:
            checksum = checksum + x
        twoscomp = ((~checksum) + 1) & 0xFF
        return twoscomp


# ============================================================================== #
#                   End DeviceBusPacket Definition                               #
#                           Begin Commands                                       #
# ============================================================================== #

class DumpCommand(DeviceBusPacket):
    """ DumpCommand is a special DeviceBusPacket that has a data field of 'D' and
    is used to retrieve board and device info for a given board or all boards.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01):
        """ Three ways to initialize the command - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for testing with the
        emulator). Alternately, a byte buffer (data_bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object. Finally, a DumpCommand may be constructed from a
        board_id and sequence number - this is what is most likely to be used
        by a client application (e.g. the flask server).
        """
        if serial_reader is not None:
            super(DumpCommand, self).__init__(serial_reader=serial_reader)
        elif data_bytes is not None:
            super(DumpCommand, self).__init__(data_bytes=data_bytes)
        else:
            super(DumpCommand, self).__init__(sequence=sequence, device_type=0xFF, board_id=board_id,
                                              device_id=0xFFFF, data=[ord('D')])


class DumpResponse(DeviceBusPacket):
    """ DumpResponse is a special DeviceBusPacket that has a data field
    containing a record for a device on a given board.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01,
                 device_id=0x0000, device_type=0x00, data=None, expected_sequence=None):
        """ Three ways to initialize the response - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for use in client apps
        that expect a response over serial, such as the flask server).
        Alternately, a byte buffer (data_bytes) may be given to the constructor,
        which is deserialized and populates the appropriate fields of the
        object. Finally, a DumpResponse may be constructed from a board_id,
        sequence number, device_id, device_type and data - this is what is
        most likely to be used when simulating responses (e.g. in the emulator).
        """
        if serial_reader is not None:
            super(DumpResponse, self).__init__(serial_reader=serial_reader, expected_sequence=expected_sequence)
        elif data_bytes is not None:
            super(DumpResponse, self).__init__(data_bytes=data_bytes)
        else:
            super(DumpResponse, self).__init__(board_id=board_id, sequence=sequence, device_id=device_id,
                                               device_type=device_type, data=data)


class VersionCommand(DeviceBusPacket):
    """ VersionCommand is a special DeviceBusPacket that has a data field of 'V' and
    is used to retrieve the version of a given board_id.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01):
        """ Three ways to initialize the command - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for testing with the
        emulator).  Alternately, a byte buffer (data_bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object. Finally, a VersionCommand may be constructed from a
        board_id and sequence number - this is what is most likely to be used
        by a client application (e.g. the flask server).
        """
        if serial_reader is not None:
            super(VersionCommand, self).__init__(serial_reader=serial_reader)
        elif data_bytes is not None:
            super(VersionCommand, self).__init__(data_bytes=data_bytes)
        else:
            super(VersionCommand, self).__init__(sequence=sequence, device_type=0xFF, board_id=board_id,
                                                 device_id=0xFFFF, data=[ord('V')])


class VersionResponse(DeviceBusPacket):
    """ VersionResponse is a special DeviceBusPacket that has a data field
    containing the version string for a given board.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01, version_string=None,
                 expected_sequence=None):
        """ Three ways to initialize the response - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for use in client apps
        that expect a response over serial, such as the flask server).
        Alternately, a byte buffer (data_bytes) may be given to the constructor,
        which is deserialized and populates the appropriate fields of the
        object. Finally, a VersionResponse may be constructed from a board_id,
        sequence number and version_string - this is what is most likely to be
        used when simulating responses (e.g. in the emulator).
        """
        if serial_reader is not None:
            super(VersionResponse, self).__init__(serial_reader=serial_reader, expected_sequence=expected_sequence)
            self.versionString = ''
            for x in self.data:
                self.versionString += chr(x)
        elif data_bytes is not None:
            super(VersionResponse, self).__init__(data_bytes=data_bytes)
            self.versionString = ''
            for x in self.data:
                self.versionString += chr(x)
        elif version_string is not None:
            data = [ord(x) for x in version_string]
            super(VersionResponse, self).__init__(sequence=sequence, device_type=0xFF, board_id=board_id,
                                                  device_id=0xFFFF, data=data)
            self.versionString = version_string
        else:
            raise BusDataException('VersionResponse requires serial_reader, data_bytes, or a version_string.')


class DeviceReadCommand(DeviceBusPacket):
    """ DeviceReadCommand is a special DeviceBusPacket that has a data field of 'R'
    and is used to retrieve the reading of a given board_id, device_id, device_type
    combination.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01,
                 device_type=0xFF, device_id=0xFFFF):
        """ Three ways to initialize the command - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for testing with the
        emulator). Alternately, a byte buffer (data_bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object. Finally, a DeviceReadCommand may be constructed from a
        board_id, device_type and device_id (and sequence number) - this is what
        is most likely to be used by a client application (e.g. the flask server).
        """
        if serial_reader is not None:
            super(DeviceReadCommand, self).__init__(serial_reader=serial_reader)
        elif data_bytes is not None:
            super(DeviceReadCommand, self).__init__(data_bytes=data_bytes)
        else:
            super(DeviceReadCommand, self).__init__(sequence=sequence, device_type=device_type, board_id=board_id,
                                                    device_id=device_id, data=[ord('R')])


class DeviceReadResponse(DeviceBusPacket):
    """ DeviceReadResponse is a special DeviceBusPacket that has a data field
    containing the device/data returned for a given board and device_id.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01,
                 device_type=0xFF, device_id=0xFFFF, device_reading=None, expected_sequence=None):
        """ Three ways to initialize the response - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for use in client apps
        that expect a response over serial, such as the flask server).
        Alternately, a byte buffer (data_bytes) may be given to the constructor, which
        is deserialized and populates the appropriate fields of the object.
        Finally, a DeviceReadResponse may be constructed from a board_id, sequence
        number and device_reading - this is what is most likely to be used when
        simulating responses (e.g. in the emulator).
        """
        if serial_reader is not None:
            super(DeviceReadResponse, self).__init__(serial_reader=serial_reader, expected_sequence=expected_sequence)
        elif device_reading is not None:
            super(DeviceReadResponse, self).__init__(sequence=sequence, device_type=device_type, board_id=board_id,
                                                     device_id=device_id, data=device_reading)
        elif data_bytes is not None:
            super(DeviceReadResponse, self).__init__(data_bytes=data_bytes)
        else:
            raise BusDataException('DeviceReadResponse requires serial_reader, data_bytes or device_reading.')


class DeviceWriteCommand(DeviceBusPacket):
    """ DeviceWriteCommand is a special DeviceBusPacket that has a data field of 'W'
    and is used to send data to a given board_id, device_id, device_type combination.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01,
                 device_type=0xFF, raw_data=None, device_id=0xFFFF):
        """ Three ways to initialize the command - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for testing with the
        emulator). Alternately, a byte buffer (data_bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object. Finally, a DeviceWriteCommand may be constructed from a
        board_id, device_type, raw_value, and device_id (and sequence number) - this is what
        is most likely to be used by a client application (e.g. the flask server).
        """
        if serial_reader is not None:
            super(DeviceWriteCommand, self).__init__(serial_reader=serial_reader)
        elif data_bytes is not None:
            super(DeviceWriteCommand, self).__init__(data_bytes=data_bytes)
        else:
            data_val = [ord('W')]
            if raw_data is not None and isinstance(raw_data, basestring):
                # TODO: this is a temporary workaround until fan motor pole is settled
                if device_type == get_device_type_code('fan_speed'):
                    data_val.append(0xFF)
                for c in raw_data:
                    data_val.append(ord(c))
            else:
                raise BusDataException('Invalid data provided to be written to device.')
            super(DeviceWriteCommand, self).__init__(sequence=sequence, device_type=device_type, board_id=board_id,
                                                     device_id=device_id, data=data_val)


class DeviceWriteResponse(DeviceBusPacket):
    """ DeviceWriteResponse is a special DeviceBusPacket that has a data field
    containing the data returned for a write operation.  Typically W1 is succeeded, W0 is failed, as
    is no response.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01,
                 device_type=0xFF, device_id=0xFFFF, device_response=None, expected_sequence=None):
        """ Three ways to initialize the response - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for use in client apps
        that expect a response over serial, such as the flask server).
        Alternately, a byte buffer (data_bytes) may be given to the constructor, which
        is deserialized and populates the appropriate fields of the object.
        Finally, a DeviceWriteResponse may be constructed from a board_id, sequence
        number and device_response - this is what is most likely to be used when
        simulating responses (e.g. in the emulator).
        """
        if serial_reader is not None:
            super(DeviceWriteResponse, self).__init__(serial_reader=serial_reader, expected_sequence=expected_sequence)
        elif device_response is not None:
            super(DeviceWriteResponse, self).__init__(sequence=sequence, device_type=device_type, board_id=board_id,
                                                      device_id=device_id, data=device_response)
        elif data_bytes is not None:
            super(DeviceWriteResponse, self).__init__(data_bytes=data_bytes)
        else:
            raise BusDataException('DeviceWriteResponse requires serial_reader, data_bytes or device_response.')


class PowerControlCommand(DeviceBusPacket):
    """ PowerControlCommand is a special DeviceBusPacket that has a data field of
    'P0' or 'P1', and is used to control the power state of a given board_id
    and device_id combination.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01, device_type=0xFF,
                 device_id=0xFFFF, power_action=None):
        """ Three ways to initialize the command - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for testing with the
        emulator).  Alternately, a byte buffer (data_bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object.  Finally, a PowerStatusCommand may be constructed from a
        board_id and device_id (and sequence number) - this is what is most
        likely to be used by a client application (e.g. the flask server).

        The power_action param may be 'on', 'off', 'cycle' or 'status'.
        """
        if serial_reader is not None:
            super(PowerControlCommand, self).__init__(serial_reader=serial_reader)
        elif data_bytes is not None:
            super(PowerControlCommand, self).__init__(data_bytes=data_bytes)
        else:
            data_val = [ord('P')]
            if power_action == 'on':
                data_val.append(ord('1'))
            elif power_action == 'off':
                data_val.append(ord('0'))
            elif power_action == 'cycle':
                data_val.append(ord('C'))
            elif power_action == 'status':
                data_val.append(ord('?'))
            else:
                raise BusDataException('Invalid power control status value provided.')
            super(PowerControlCommand, self).__init__(sequence=sequence, device_type=device_type, board_id=board_id,
                                                      device_id=device_id, data=data_val)


class PowerControlResponse(DeviceBusPacket):
    """ PowerControlResponse is a special DeviceBusPacket that has a data field
    containing the result of a power control action for a given board and device_id.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01, device_type=0xFF,
                 device_id=0xFFFF, data=None, expected_sequence=None):
        """ Three ways to initialize the response - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for use in client apps
        that expect a response over serial, such as the flask server).
        Alternately, a byte buffer (data_bytes) may be given to the constructor,
        which is deserialized and populates the appropriate fields of the
        object. Finally, a PowerControlResponse may be constructed from a
        board_id, sequence number and data - this is what is most likely to
        be used when simulating responses (e.g. in the emulator).
        """
        if serial_reader is not None:
            super(PowerControlResponse, self).__init__(serial_reader=serial_reader, expected_sequence=expected_sequence)
        elif data is not None:
            super(PowerControlResponse, self).__init__(sequence=sequence, device_type=device_type, board_id=board_id,
                                                       device_id=device_id, data=data)
        elif data_bytes is not None:
            super(PowerControlResponse, self).__init__(data_bytes=data_bytes)
        else:
            raise BusDataException('PowerControlResponse requires serial_reader, data_bytes or data.')


class ChamberLedControlCommand(DeviceBusPacket):
    """ ChamberLedControlCommand is a special DeviceBusPacket that has a data field beginning with 'L'
    and is used to control the state of a given rack's chamber LED.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01, device_type=0xFF,
                 device_id=0xFFFF, led_state=None, led_color=None, rack_id=None, blink_state=None):
        """ Three ways to initialize the command - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for testing with the
        emulator).  Alternately, a byte buffer (data_bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object.  Finally, a ChamberLedControlCommand may be constructed from a
        board_id and device_id (and sequence number) - this is what is most
        likely to be used by a client application (e.g. the flask server).

        Led_state, led_color, rack_id, and blink_state are all required.
        """
        if serial_reader is not None:
            super(ChamberLedControlCommand, self).__init__(serial_reader=serial_reader)
        elif data_bytes is not None:
            super(ChamberLedControlCommand, self).__init__(data_bytes=data_bytes)
        else:
            led_string = 'L'

            # TODO: when PLC comms finalized, this will likely change
            # format example: 'L-1,3,ffffff,1' ==> state no override, rack 3, color ffffff, blink
            if led_state == 'no_override':
                led_string += '-1,'
            elif led_state == 'on':
                led_string += '1,'
            elif led_state == 'off':
                led_string += '0,'
            else:
                raise BusDataException('Invalid led_state provided.')
            led_string += str(rack_id) + ','
            if led_color == 'no_override':
                led_string += '-1,'
            else:
                led_string += led_color + ','
            if blink_state == 'no_override':
                led_string += '-1'
            elif blink_state == 'blink':
                led_string += '1'
            elif blink_state == 'steady':
                led_string += '0'
            else:
                raise BusDataException('Invalid led blink_state provided.')

            logger.warning('LED STRING: {}'.format(led_string))
            data_val = [ord(x) for x in led_string]

            super(ChamberLedControlCommand, self).__init__(sequence=sequence, device_type=device_type,
                                                           board_id=board_id, device_id=device_id, data=data_val)


class ChamberLedControlResponse(DeviceBusPacket):
    """ PowerControlResponse is a special DeviceBusPacket that has a data field
    containing the result of a power control action for a given board and device_id.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01, device_type=0xFF,
                 device_id=0xFFFF, data=None, expected_sequence=None):
        """ Three ways to initialize the response - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for use in client apps
        that expect a response over serial, such as the flask server).
        Alternately, a byte buffer (data_bytes) may be given to the constructor,
        which is deserialized and populates the appropriate fields of the
        object. Finally, a PowerControlResponse may be constructed from a
        board_id, sequence number and data - this is what is most likely to
        be used when simulating responses (e.g. in the emulator).
        """
        if serial_reader is not None:
            super(ChamberLedControlResponse, self).__init__(serial_reader=serial_reader,
                                                            expected_sequence=expected_sequence)
        elif data is not None:
            super(ChamberLedControlResponse, self).__init__(sequence=sequence, device_type=device_type,
                                                            board_id=board_id, device_id=device_id, data=data)
        elif data_bytes is not None:
            super(ChamberLedControlResponse, self).__init__(data_bytes=data_bytes)
        else:
            raise BusDataException('PowerControlResponse requires serial_reader, data_bytes or data.')


class BootTargetCommand(DeviceBusPacket):
    """ BootTargetCommand is a special DeviceBusPacket that has a data field of
    'B?', 'B0', 'B1' or 'B2', and is used to control the boot target of a given board_id
    and device_id combination.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01, device_type=0xFF,
                 device_id=0xFFFF, boot_target=None):
        """ Three ways to initialize the command - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for testing with the
        emulator).  Alternately, a byte buffer (data_bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object.  Finally, a BootTargetCommand may be constructed from a
        board_id and device_id (and sequence number) - this is what is most
        likely to be used by a client application (e.g. the flask server).

        The boot_target param may be 'no_override', 'hdd', 'pxe' or 'status'.
        """
        if serial_reader is not None:
            super(BootTargetCommand, self).__init__(serial_reader=serial_reader)
        elif data_bytes is not None:
            super(BootTargetCommand, self).__init__(data_bytes=data_bytes)
        else:
            data_val = [ord('B')]
            if boot_target == 'no_override':
                data_val.append(ord('0'))
            elif boot_target == 'hdd':
                data_val.append(ord('1'))
            elif boot_target == 'pxe':
                data_val.append(ord('2'))
            elif boot_target == 'status':
                data_val.append(ord('?'))
            else:
                raise BusDataException('Invalid boot target value provided.')
            super(BootTargetCommand, self).__init__(sequence=sequence, device_type=device_type, board_id=board_id,
                                                    device_id=device_id, data=data_val)


class BootTargetResponse(DeviceBusPacket):
    """ BootTargetResponse is a special DeviceBusPacket that has a data field
    containing the result of a boot target action for a given board and device_id.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01, device_type=0xFF,
                 device_id=0xFFFF, data=None, expected_sequence=None):
        """ Three ways to initialize the response - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for use in client apps
        that expect a response over serial, such as the flask server).
        Alternately, a byte buffer (data_bytes) may be given to the constructor,
        which is deserialized and populates the appropriate fields of the
        object. Finally, a BootTargetResponse may be constructed from a
        board_id, sequence number and data - this is what is most likely to
        be used when simulating responses (e.g. in the emulator).
        """
        if serial_reader is not None:
            super(BootTargetResponse, self).__init__(serial_reader=serial_reader, expected_sequence=expected_sequence)
        elif data is not None:
            super(BootTargetResponse, self).__init__(sequence=sequence, device_type=device_type, board_id=board_id,
                                                     device_id=device_id, data=data)
        elif data_bytes is not None:
            super(BootTargetResponse, self).__init__(data_bytes=data_bytes)
        else:
            raise BusDataException('BootTargetResponse requires serial_reader, data_bytes or data.')


class AssetInfoCommand(DeviceBusPacket):
    """ AssetInfoCommand is a special DeviceBusPacket that has a data field of
    'A', and is used to get asset information for a given board_id and device_id combination.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01, device_type=0xFF,
                 device_id=0xFFFF):
        """ Three ways to initialize the command - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for testing with the
        emulator).  Alternately, a byte buffer (data_bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object.  Finally, an AssetInfoCommand may be constructed from a
        board_id and device_id (and sequence number) - this is what is most
        likely to be used by a client application (e.g. the flask server).
        """
        if serial_reader is not None:
            super(AssetInfoCommand, self).__init__(serial_reader=serial_reader)
        elif data_bytes is not None:
            super(AssetInfoCommand, self).__init__(data_bytes=data_bytes)
        else:
            data_val = [ord('A')]
            super(AssetInfoCommand, self).__init__(sequence=sequence, device_type=device_type, board_id=board_id,
                                                   device_id=device_id, data=data_val)


class AssetInfoResponse(DeviceBusPacket):
    """ AssetInfoResponse is a special DeviceBusPacket that has a data field
    containing the result of a get asset info command for a given board and device_id.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01, device_type=0xFF,
                 device_id=0xFFFF, data=None, expected_sequence=None):
        """ Three ways to initialize the response - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for use in client apps
        that expect a response over serial, such as the flask server).
        Alternately, a byte buffer (data_bytes) may be given to the constructor,
        which is deserialized and populates the appropriate fields of the
        object. Finally, an AssetInfoResponse may be constructed from a
        board_id, sequence number and data - this is what is most likely to
        be used when simulating responses (e.g. in the emulator).
        """
        if serial_reader is not None:
            super(AssetInfoResponse, self).__init__(serial_reader=serial_reader, expected_sequence=expected_sequence)
        elif data is not None:
            super(AssetInfoResponse, self).__init__(sequence=sequence, device_type=device_type, board_id=board_id,
                                                    device_id=device_id, data=data)
        elif data_bytes is not None:
            super(AssetInfoResponse, self).__init__(data_bytes=data_bytes)
        else:
            raise BusDataException('AssetInfoResponse requires serial_reader, data_bytes or data.')


class RetryCommand(DeviceBusPacket):
    """ RetryCommand is a special DeviceBusPacket that has a data field of '?'
    and is used to retrieve the last known good response from firmware - e.g.
    in the case of line noise corrupting a response.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01,
                 device_type=0xFF, device_id=0xFFFF):
        """ Three ways to initialize the command - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for testing with the
        emulator). Alternately, a byte buffer (data_bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object. Finally, a RetryCommand may be constructed from a
        board_id, device_type and device_id (and sequence number) - this is what
        is most likely to be used by a client application (e.g. the flask server).
        """
        if serial_reader is not None:
            super(RetryCommand, self).__init__(serial_reader=serial_reader)
        elif data_bytes is not None:
            super(RetryCommand, self).__init__(data_bytes=data_bytes)
        else:
            super(RetryCommand, self).__init__(sequence=sequence, device_type=device_type, board_id=board_id,
                                               device_id=device_id, data=[ord('?')])

# ======================================================================================================================
#                                           Begin Temporary Commands
# ======================================================================================================================


class HostInfoCommand(DeviceBusPacket):
    """ HostInfoCommand is a special (temporary) DeviceBusPacket that has a data field beginning with 'H'
    and is used to get ip address and hostname from a 'system' device type.  In real PLC comms, TTY will be used
    to retrieve this information.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01, device_type=0xFF,
                 device_id=0xFFFF):
        """ Three ways to initialize the command - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for testing with the
        emulator).  Alternately, a byte buffer (data_bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object.  Finally, a HostInfoCommand may be constructed from a
        board_id and device_id (and sequence number) - this is what is most
        likely to be used by a client application (e.g. the flask server).

        """
        if serial_reader is not None:
            super(HostInfoCommand, self).__init__(serial_reader=serial_reader)
        elif data_bytes is not None:
            super(HostInfoCommand, self).__init__(data_bytes=data_bytes)
        else:
            data_val = [ord('H')]
            super(HostInfoCommand, self).__init__(sequence=sequence, device_type=device_type, board_id=board_id,
                                                  device_id=device_id, data=data_val)


class HostInfoResponse(DeviceBusPacket):
    """ HostInfoResponse is a special (temporary) DeviceBusPacket that has a data field
    containing the result of a host info action for a given board and device_id where device_type is 'system'.
    """
    def __init__(self, serial_reader=None, board_id=0x00000000, data_bytes=None, sequence=0x01, device_type=0xFF,
                 device_id=0xFFFF, data=None, expected_sequence=None):
        """ Three ways to initialize the response - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for use in client apps
        that expect a response over serial, such as the flask server).
        Alternately, a byte buffer (data_bytes) may be given to the constructor,
        which is deserialized and populates the appropriate fields of the
        object. Finally, a HostInfoResponse may be constructed from a
        board_id, sequence number and data - this is what is most likely to
        be used when simulating responses (e.g. in the emulator).
        """
        if serial_reader is not None:
            super(HostInfoResponse, self).__init__(serial_reader=serial_reader, expected_sequence=expected_sequence)
        elif data is not None:
            super(HostInfoResponse, self).__init__(sequence=sequence, device_type=device_type, board_id=board_id,
                                                   device_id=device_id, data=data)
        elif data_bytes is not None:
            super(HostInfoResponse, self).__init__(data_bytes=data_bytes)
        else:
            raise BusDataException('HostInfoResponse requires serial_reader, data_bytes or data.')
