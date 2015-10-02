#!/usr/bin/python
"""
   OpenDCRE Device Bus Module
   Author:  andrew, steven
   Date:    4/13/2015
   Update:  6/11/2015 - Add power control, remap from sensors to devices. (ABC)

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

import logging

import serial

DEBUG = False
logger = logging.getLogger()

# ============================================================================== #
#                     Begin DeviceBusPacket Definition                           #
# ============================================================================== #


class DeviceBusPacket(object):
    """
    DeviceBusPacket is a representation of a single packet that travels the
    device bus.
    """
    def __init__(self, serial_reader=None, bytes=None, sequence=0x01, device_type=0xFF,
                 board_id=0xFF, port_id=0xFF, device_id=0xFF, data=None):
        """
        Construct a new DeviceBusPacket. There are three real ways to do this -
        either via the bytes parameter, or via the individual fields of
        the packet itself (in that case, the header, length, checksum and
        trailer are all automatically generated). Data must be a list of bytes.
        The third way is to use serial_reader, which will read a generic packet
        from the serial stream.
        """
        if serial_reader is not None:
            # this routine will read from serial into a buffer as follows:
            # get header and length bytes
            try:
                serialbytes = []
                serialbytes.append(ord(serial_reader.read(1)))
                serialbytes.append(ord(serial_reader.read(1)))
                # read length bytes
                for x in serial_reader.read(serialbytes[1]):
                    serialbytes.append(ord(x))
                # read one byte for trailer
                serialbytes.append(ord(serial_reader.read(1)))
                # now make the packet
                # print [hex(x) for x in bytes]
                self.deserialize(serialbytes)
            except Exception:
                # yes, this is a catchall exception, however:
                # if something bad happened, it is related to reading
                # junk or nothing at all from the bus.  in either case, we can
                # not recover, so our only choice is to pass a
                # BusTimeoutException up the chain for handling
                raise BusTimeoutException("No response from bus.")
        elif bytes is not None:
            # if we have a raw packet to build off of,
            # populate our fields with the deserialized result
            # self.packetBytes=packetBytes       # ABC: removed, not needed
            self.deserialize(bytes)
        else:
            # otherwise, we populate our fields as provided by the user
            self.sequence = sequence
            self.device_type = device_type
            self.board_id = board_id
            self.port_id = port_id
            self.device_id = device_id
            if isinstance(data, list):
                self.data = data
            else:
                self.data = [data]

    def serialize(self, sequence=None, device_type=None, board_id=None, port_id=None, device_id=None, data=None):
        """
        Generate a serialized byte representation of the given packet, or of a
        packet created on the fly using the provided parameters.  If a
        parametrized serialization is desired, then ALL of the packet fields
        must be specified.  Otherwise, if none of the fields are specified, then
        the fields of this packet instance are serialized.
        """
        if not sequence and not device_type and not board_id and not port_id and not device_id and not data:
            sequence = self.sequence
            device_type = self.device_type
            board_id = self.board_id
            port_id = self.port_id
            device_id = self.device_id
            data = self.data
        else:
            raise BusDataException("All fields of a packet must be specified in order to be serialized.")

        # find length of packet. Since sequence through device id and checksum
        # are always 1 byte add those up to 6.
        length = 6 + len(data)
        # generate checksum over packet contents
        checksum = self.generateChecksum(sequence, device_type, board_id, port_id, device_id, data)
        # construct and return packet
        packet = [0x01, length, sequence, device_type, board_id, port_id, device_id]
        for x in data:
            packet.append(x)
        packet.append(checksum)
        packet.append(0x04)
        return packet

    def deserialize(self, packetBytes):
        """
        Populate the fields of a DeviceBusPacket instance
        """
        # check length to make sure we have at minimum the min packet length
        if len(packetBytes) < 9:
            raise BusDataException("Invalid packet byte stream length of " + str(len(packetBytes)))

        # check header byte - if invalid, toss
        if packetBytes[0] != 0x01:
            raise BusDataException("No header byte found in incoming packet.")

        # check length - if packetBytes len doesn't match, toss
        if packetBytes[1] != len(packetBytes) - 3:
            raise BusDataException("Invalid length from incoming packet.")

        # get sequence num
        self.sequence = packetBytes[2]

        # get device type
        self.device_type = packetBytes[3]

        # get board id
        self.board_id = packetBytes[4]

        # get port id
        self.port_id = packetBytes[5]

        # get device id
        self.device_id = packetBytes[6]

        # get data (up to 32 bytes) - todo multi-packet transmissions
        self.data = []
        for x in packetBytes[7:len(packetBytes) - 2]:
            self.data.append(x)

        # get the checksum and verify it - toss if no good
        if (self.generateChecksum(self.sequence, self.device_type, self.board_id,
                                  self.port_id, self.device_id, self.data) != packetBytes[len(packetBytes) - 2]):
            raise BusDataException("Invalid checksum in incoming packet.")

        # get the trailer byte - toss if no good
        if packetBytes[len(packetBytes) - 1] != 0x04:
            raise BusDataException("Invalid trailer byte found in incoming packet.")
        # if we make it here, the packet successfully was deserialized!

    def generateChecksum(self, sequence, device_type, board_id, port_id, device_id, data):
        """
        Generate and return packet checksum given its fields.  Twos complement
        of 0xFF & the sum of bytes from devicetype to data end.
        """
        checksum = sequence + device_type + board_id + port_id + device_id
        for x in data:
            checksum = checksum + x
        twoscomp = ((~checksum) + 1) & 0xFF
        return twoscomp


# ============================================================================== #
#                   End DeviceBusPacket Definition                               #
#                           Begin Commands                                       #
# ============================================================================== #


class DumpCommand(DeviceBusPacket):
    """
    DumpCommand is a special DeviceBusPacket that has a data field of 'D' and
    is used to retrieve board and port info for a given board or all boards.
    """
    def __init__(self, serial_reader=None, board_id=0xFF, bytes=None, sequence=0x01):
        """
        Three ways to initialize the command - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for testing with the
        emulator).  Alternately, a byte buffer (bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object.  Finally, a DumpCommand may be constructed from a
        board_id and sequence number - this is what is most likely to be used
        by a client application (e.g. the flask server).
        """
        if serial_reader is not None:
            super(DumpCommand, self).__init__(serial_reader=serial_reader)
        elif bytes is not None:
            super(DumpCommand, self).__init__(bytes=bytes)
        else:
            super(DumpCommand, self).__init__(sequence=sequence, device_type=0xFF,
                            board_id=board_id, port_id=0xFF, device_id=0xFF, data=[ord('D')])


class DumpResponse(DeviceBusPacket):
    """
    DumpResponse is a special DeviceBusPacket that has a data field
    containing a record for a device port on a given board.
    """
    def __init__(self, serial_reader=None, board_id=0x00, bytes=None, sequence=0x01,
                 port_id=0x00, device_id=0x00, device_type=0x00, data=None):
        """
        Three ways to initialize the response - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for use in client apps
        that expect a response over serial, such as the flask server).
        Alternately, a byte buffer (bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object.  Finally, a DumpResponse may be constructed from a
        board_id, sequence number, port_id, device_id, device_type and data -
        this is what is most likely to be used when simulating responses
        (e.g. in the emulator).
        """
        if serial_reader is not None:
            super(DumpResponse, self).__init__(serial_reader=serial_reader)
        elif bytes is not None:
            super(DumpResponse, self).__init__(bytes=bytes)
        else:
            super(DumpResponse, self).__init__(board_id=board_id, sequence=sequence, port_id=port_id,
                            device_id=device_id, device_type=device_type, data=data)


class VersionCommand(DeviceBusPacket):
    """
    VersionCommand is a special DeviceBusPacket that has a data field of 'V' and
    is used to retrieve the version of a give board_id.
    """
    def __init__(self, serial_reader=None, board_id=0x00, bytes=None, sequence=0x01):
        """
        Three ways to initialize the command - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for testing with the
        emulator).  Alternately, a byte buffer (bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object.  Finally, a VersionCommand may be constructed from a
        board_id and sequence number - this is what is most likely to be used
        by a client application (e.g. the flask server).
        """
        if serial_reader is not None:
            super(VersionCommand, self).__init__(serial_reader=serial_reader)
        elif bytes is not None:
            super(VersionCommand, self).__init__(bytes=bytes)
        else:
            super(VersionCommand, self).__init__(sequence=sequence, device_type=0xFF,
                            board_id=board_id, port_id=0xFF, device_id=0xFF, data=[ord('V')])


class VersionResponse(DeviceBusPacket):
    """
    VersionResponse is a special DeviceBusPacket that has a data field
    containing the version string for a given board.
    """
    def __init__(self, serial_reader=None, board_id=0x00, bytes=None, sequence=0x01, versionString=None):
        """
        Three ways to initialize the response - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for use in client apps
        that expect a response over serial, such as the flask server).
        Alternately, a byte buffer (bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object.  Finally, a VersionResponse may be constructed from a
        board_id, sequence number and versionString - this is what is most
        likely to be used when simulating responses (e.g. in the emulator).
        """
        if serial_reader is not None:
            super(VersionResponse, self).__init__(serial_reader=serial_reader)
            self.versionString = ""
            for x in self.data:
                self.versionString += chr(x)
        elif bytes is not None:
            super(VersionResponse, self).__init__(bytes=bytes)
            self.versionString = ""
            for x in self.data:
                self.versionString += chr(x)
        elif versionString is not None:
            data = [ord(x) for x in versionString]
            super(VersionResponse, self).__init__(sequence=sequence, device_type=0xFF,
                        board_id=board_id, port_id=0xFF, device_id=0xFF, data=data)
            self.versionString = versionString
        else:
            raise BusDataException("VersionResponse requires serial_reader, bytes, or a versionString.")


class DeviceReadCommand(DeviceBusPacket):
    """
    DeviceReadCommand is a special DeviceBusPacket that has a data field of 'R'
    and is used to retrieve the reading of a given board_id,port_id,device_id,
    device_type combination.
    """
    def __init__(self, serial_reader=None, board_id=0x00, bytes=None, sequence=0x01,
                 device_type=0xFF, port_id=0xFF, device_id=0xFF):
        """
        Three ways to initialize the command - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for testing with the
        emulator).  Alternately, a byte buffer (bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object.  Finally, a DeviceReadCommand may be constructed from a
        board_id, port_id, device_type and device_id (and sequence number) -
        this is what is most likely to be used by a client application
        (e.g. the flask server).
        """
        if serial_reader is not None:
            super(DeviceReadCommand, self).__init__(serial_reader=serial_reader)
        elif bytes is not None:
            super(DeviceReadCommand, self).__init__(bytes=bytes)
        else:
            super(DeviceReadCommand, self).__init__(sequence=sequence, device_type=device_type,
                                board_id=board_id, port_id=port_id, device_id=device_id, data=[ord('R')])


class DeviceReadResponse(DeviceBusPacket):
    """
    DeviceReadResponse is a special DeviceBusPacket that has a data field
    containing the device/ data returned for a given board, port and
    device_id.
    """
    def __init__(self, serial_reader=None, board_id=0x00, bytes=None, sequence=0x01,
                 device_type=0xFF, port_id=0xFF, device_id=0xFF, device_reading=None):
        """
        Three ways to initialize the response - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for use in client apps
        that expect a response over serial, such as the flask server).
        Alternately, a byte buffer (bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object.  Finally, a DeviceReadResponse may be constructed from a
        board_id, sequence number and device_reading - this is what is most
        likely to be used when simulating responses (e.g. in the emulator).
        """
        if serial_reader is not None:
            super(DeviceReadResponse, self).__init__(serial_reader=serial_reader)
        elif device_reading is not None:
            super(DeviceReadResponse, self).__init__(sequence=sequence,
                    device_type=device_type, board_id=board_id, port_id=port_id,
                    device_id=device_id, data=device_reading)
        elif bytes is not None:
            super(DeviceReadResponse, self).__init__(bytes=bytes)
        else:
            raise BusDataException("DeviceReadResponse requires serial_reader, bytes or device_reading.")


class PowerControlCommand(DeviceBusPacket):
    """
    PowerControlCommand is a special DeviceBusPacket that has a data field of
    'P0' or 'P1', and is used to control the power state of a given board_id,
    port_id, device_id, combination.
    """
    def __init__(self, serial_reader=None, board_id=0x00, bytes=None, sequence=0x01,
                 device_type=0xFF, port_id=0xFF, device_id=0xFF, power_on=False,
                 power_off=False, power_cycle=False, power_status=False):
        """
        Three ways to initialize the command - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for testing with the
        emulator).  Alternately, a byte buffer (bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object.  Finally, a PowerStatusCommand may be constructed from a
        board_id, port_id, and device_id (and sequence number) -
        this is what is most likely to be used by a client application
        (e.g. the flask server).
        Either power_on, power_off or power_cycle may be specified as True.
        If power_on is specified as True, then a power_on command is sent.
        If power_off is specified as True, then a power_off command is sent.
        If power_cycle is specified as True, then a power_cycle command is sent.
        If power_status is specified as True, then a power_status command is
        sent.
        """
        if serial_reader is not None:
            super(PowerControlCommand, self).__init__(serial_reader=serial_reader)
        elif bytes is not None:
            super(PowerControlCommand, self).__init__(bytes=bytes)
        else:
            dataVal = [ord('P')]
            if power_on is True and power_off is False and power_cycle is False and power_status is False:
                dataVal.append(ord('1'))
            elif power_on is False and power_off is True and power_cycle is False and power_status is False:
                dataVal.append(ord('0'))
            elif power_on is False and power_off is False and power_cycle is True and power_status is False:
                dataVal.append(ord('C'))
            elif power_on is False and power_off is False and power_cycle is False and power_status is True:
                dataVal.append(ord('?'))
            else:
                raise BusDataException("Only one power control action may be specified as True.")
            super(PowerControlCommand, self).__init__(sequence=sequence, device_type=device_type,
                                board_id=board_id, port_id=port_id, device_id=device_id, data=dataVal)


class PowerControlResponse(DeviceBusPacket):
    """
    PowerControlResponse is a special DeviceBusPacket that has a data field
    containing the result of a power control action for a given board, port and
    device_id.
    """
    def __init__(self, serial_reader=None, board_id=0x00, bytes=None, sequence=0x01, device_type=0xFF,
                 port_id=0xFF, device_id=0xFF, data=None):
        """
        Three ways to initialize the response - it may be read, when expected,
        via a serial reader (via serial_reader - e.g. for use in client apps
        that expect a response over serial, such as the flask server).
        Alternately, a byte buffer (bytes) may be given to the
        constructor, which is deserialized and populates the appropriate fields
        of the object.  Finally, a PowerControlResponse may be constructed from a
        board_id, sequence number and data - this is what is most
        likely to be used when simulating responses (e.g. in the emulator).
        """
        if serial_reader is not None:
            super(PowerControlResponse, self).__init__(serial_reader=serial_reader)
        elif data is not None:
            super(PowerControlResponse, self).__init__(sequence=sequence, device_type=device_type,
                            board_id=board_id, port_id=port_id, device_id=device_id, data=data)
        elif bytes is not None:
            super(PowerControlResponse, self).__init__(bytes=bytes)
        else:
            raise BusDataException("PowerControlResponse requires serial_reader, bytes or data.")


# ============================================================================== #
#                                   End Commands                                 #
#                        Begin Support Objects and Methods                       #
# ============================================================================== #


class BusTimeoutException(Exception):
    """
    Exception raised when a command fails to receive
    a response from the device bus.  This may be for
    many reasons, which it may be difficult or impossible
    to pinpoint, so no more specific error is available.
    """
    pass


class BusDataException(Exception):
    """
    Exception raised when something sent over the bus does not look right.
    """
    pass


def initialize(serial_device, speed=9600, timeout=0.25):
    """ initialize - get serial connection on given serial port.

    Args:  serial_device is the device entry to use in opening/initializing
    the serial connection.

    Returns:  a pyserial instance to work with.
    """
    ser = serial.Serial(serial_device, speed, timeout=timeout)
    ser.flushInput()
    ser.flushOutput()
    return ser

# these are the mappings between device type names and their bus codes
device_name_codes = {
    "led"           : 0x10,
    "ipmb"          : 0x12,
    "power"         : 0x40,
    "humidity"      : 0x4E,
    "door_lock"     : 0x82,
    "current"       : 0x90,
    "temperature"   : 0x9A,
    "thermistor"    : 0x9C,
    "pressure"      : 0xEE,
    "none"          : 0xFF
}


def get_device_type_code(device_type):
    """ get_device_type_code - gets a numeric value corresponding to a string
                                value describing a device type.

        Args:  device_type - string value representing device type

        Returns:  numeric device type code.  0xFF if device_type is not
                    recognized.
    """
    global device_name_codes
    if device_type in device_name_codes:
        return device_name_codes[device_type]
    else:
        return device_name_codes["none"]


def get_device_type_name(device_code):
    """ get_device_type_name - gets a string value corresponding to a numeric
                                code representing a device type.

        Args:  device_code - the numeric device code value.

        Returns:  string device type name.  "none" if device_code is not
                    recognized.
    """
    for name in device_name_codes:
        if device_name_codes[name] == device_code:
            return name
    return "none"


def convertThermistor(adc):
    """convertThermistor - calculates a real world value from the raw data.

    Args:  adc is the value from the device to be converted.

    Returns: the thermistor temperature value, in Celsius

    """
    if adc >= 65535:
        raise BusDataException("Thermistor value > 0xFFFF received.")
    else:
        if adc > 745:
            temperature = (adc * -0.131) + 118.638
        elif adc > 542:
            temperature = (adc * -0.0985) + 93.399
        elif adc > 354:
            temperature = (adc * -0.106) + 97.66
        elif adc > 218:
            temperature = (adc * -0.147) + 112.046
        else:
            temperature = (adc * -0.235) + 131.294
        return float('%.2f' % round(temperature, 2))


def convertDirectPmbus(raw, reading_type, rSense=1.0):
    """
        Converts a raw voltage / current PMBUS value to a human-readable/real
        value.

        Args: raw is the raw PMBUS direct value, reading_type is the type of
            reading being converted.  Supported values include:
                "current", "voltage" and "power"
            rSense is the milliohm value for the sense resistor, used to
            compute m coefficient. if rSense causes m to be > 32767, then we
            must divide m by 10, and increase the R coefficient by 1 (per
            p30 of ADM1276 data sheet)

        Returns: a converted, decimal value corresponding to the raw reading.
    """
    if reading_type == "current":
        m = 807.0 * rSense
        b = 20745.0
        r = -1.0
    elif reading_type == "voltage":
        # we are operating in the 0-20V range here
        m = 19199.0
        b = 0.0
        r = -2.0
    elif reading_type == "power":
        m = 6043.0 * rSense
        b = 0.0
        r = -2.0
    else:
        raise BusDataException(
            "Invalid reading_type specified for PMBUS direct conversion.")

    return (1.0 / m) * (raw * 10.0 ** (-r) - b)
