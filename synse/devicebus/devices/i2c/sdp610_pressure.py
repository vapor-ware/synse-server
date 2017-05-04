#!/usr/bin/env python
""" Synse I2C pressure via SDP610

    Author: Andrew Cencini
    Date:   10/18/2016

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
from binascii import hexlify
import time
import lockfile
import sys

from i2c_device import I2CDevice
from sdp610_emulator import read_emulator
import synse.strings as _s_
from synse import constants as const
from synse.devicebus.constants import CommandId as cid
from synse.devicebus.response import Response
from synse.errors import SynseException

from mpsse import *

logger = logging.getLogger(__name__)

POLYNOMIAL = 0x131

# Per data sheet, Section 2
SCALE_FACTOR = 60


class SDP610Pressure(I2CDevice):
    """ Device subclass for thermistor via MAX11608 I2C ADC.
    """
    _instance_name = 'sdp-610'

    def __init__(self, **kwargs):
        super(SDP610Pressure, self).__init__(**kwargs)

        # Sensor specific commands.
        self._command_map[cid.READ] = self._read

        self._lock = lockfile.LockFile(self.serial_lock)

        self.altitude = kwargs['altitude']

        self.channel = int(kwargs['channel'], 16)

        self.board_id = int(kwargs['board_offset']) + int(kwargs['board_id_range'][0])

        self.board_record = dict()
        self.board_record['board_id'] = format(self.board_id, '08x')
        self.board_record['devices'] = [
            {
                'device_id': kwargs['device_id'],
                'device_type': 'pressure',
                'device_info': kwargs.get('device_info', 'CEC pressure')
            }
        ]

    def _read(self, command):
        """ Read the data off of a given board's device.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the read response.
        """
        # get the command data out from the incoming command
        device_id = command.data[_s_.DEVICE_ID]
        device_type_string = command.data[_s_.DEVICE_TYPE_STRING]

        try:
            # validate device to ensure device id and type are ok
            self._get_device_by_id(device_id, device_type_string)

            reading = self._read_sensor()

            if reading is not None:
                return Response(
                    command=command,
                    response_data=reading
                )

            # if we get here, there was no sensor device found, so we must raise
            logger.error('No response for sensor reading for command: {}'.format(command.data))
            raise SynseException('No sensor reading returned from I2C.')

        except Exception:
            raise SynseException('Error reading pressure sensor (device id: {})'.format(device_id)), None, sys.exc_info()[2]

    def _read_sensor(self):
        with self._lock:
            if self.hardware_type == 'emulator':
                # -- EMULATOR --> test-only code path
                # convert to an int from hex number string read from emulator
                sensor_int = int(hexlify(read_emulator(self.device_name, self.channel)), 16)

                # value is in 16 bit 2's complement
                if sensor_int & 0x8000:
                    sensor_int = (~sensor_int + 1) & 0xFFFF
                    sensor_int = -sensor_int

                return {const.UOM_PRESSURE: sensor_int * 1.0}
            else:
                # -- REAL HARDWARE --
                # Port A I2C for MAX11608
                vec = MPSSE()
                vec.Open(0x0403, 0x6011, I2C, ONE_HUNDRED_KHZ, MSB, IFACE_A)

                # Port B I2C for debug leds (don't need the io expander for the DPS sensors)
                gpio = MPSSE()
                gpio.Open(0x0403, 0x6011, I2C, ONE_HUNDRED_KHZ, MSB, IFACE_B)

                try:
                    # Set RESET line on PCA9546A to high to activate switch
                    vec.PinHigh(GPIOL0)

                    # Read channel
                    vec.Start()
                    vec.Write('\xE3')
                    if vec.GetAck() == ACK:
                        # if we got an ack then slave is there
                        vec.Read(1)
                        vec.SendNacks()
                        vec.Read(1)
                        vec.SendAcks()

                        # Set channel: Convert channel number to string and add to address
                        channel_str = '\xE2' + chr(self.channel)
                        vec.Start()
                        vec.Write(channel_str)
                        vec.Stop()

                        # verify channel was set
                        vec.Start()
                        vec.Write('\xE3')
                        vec.SendNacks()
                        reg = vec.Read(1)
                        vec.Stop()
                        if ord(reg) != self.channel:
                            raise SynseException(
                                'Failed to set I2C switch channel for pressure read. ({})'.format(ord(reg))
                            )

                        # Read DPS sensor connected to the set channel
                        vec.SendAcks()
                        vec.Start()
                        vec.Write('\x80\xF1')
                        vec.Start()
                        vec.Write('\x81')

                        # Give SDP610 time for the conversion since clock stretching is not implemented
                        time.sleep(0.005)

                        # Read the three bytes out of the DPS sensor (two data bytes and crc)
                        sense_data = vec.Read(2)
                        vec.SendNacks()
                        sense_data += vec.Read(1)
                        vec.Stop()
                        vec.SendAcks()

                        # Debug print data
                        logger.debug('Sensor Data: 0x%0.2X%0.2X%0.2X' % (ord(sense_data[0]), ord(sense_data[1]),
                                                                         ord(sense_data[2])))
                        if not self._crc8_check(sense_data):
                            raise SynseException('Sensor CRC check failed.')

                        return {const.UOM_PRESSURE: self._convert_reading(sense_data[0] + sense_data[1], self.altitude)}
                    else:
                        vec.Stop()
                        raise SynseException('I2C Bus Error: No ACK received on device initialization.')
                finally:
                    vec.Close()
                    gpio.Close()

    @staticmethod
    def _altitude_correction(altitude):
        """ Get the altitude correction factor, given an altitude in meters.

        http://www.mouser.com/ds/2/682/Sensirion_Differential_Pressure_SDP6x0series_Datas-767275.pdf

        Args:
            altitude (int): the altitude in meters above sea level.

        Returns:
            float: the altitude correction factor.
        """
        # FIXME - handling for values below 0m -- nothing specified in the datasheet,
        #   should assume anything below 0 is invalid?
        if altitude < 0:
            raise ValueError(
                'Unable to get correction factor for altitude ({}); must be >= 0'.format(altitude)
            )
        elif altitude < 250:
            corr = 0.95
        elif altitude < 425:
            corr = 0.98
        elif altitude < 500:
            corr = 1.00
        elif altitude < 750:
            corr = 1.01
        elif altitude < 1500:
            corr = 1.04
        elif altitude < 2250:
            corr = 1.15
        elif altitude < 3000:
            corr = 1.26
        else:
            corr = 1.38

        return corr

    @staticmethod
    def _convert_reading(sensor_str, altitude):
        """

        Args:
            sensor_str:
            altitude:

        Returns:

        """
        # convert to an int from hex number string
        sensor_int = int(hexlify(sensor_str), 16)

        # value is in 16 bit 2's complement
        if sensor_int & 0x8000:
            sensor_int = (~sensor_int + 1) & 0xFFFF
            sensor_int = -sensor_int

        # pressure = sensor_int / scale_factor
        return (sensor_int / SCALE_FACTOR) * SDP610Pressure._altitude_correction(altitude)

    @staticmethod
    def _crc8_check(data):
        """ CRC checker, data must be in string form which is the output of the sensor

        Args:
            data: Data to check CRC of

        Returns:
            bool: True if CRC check passes, False otherwise
        """
        crc = 0
        for x in range(len(data) - 1):
            crc ^= ord(data[x])
            for y in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ POLYNOMIAL
                else:
                    crc = (crc << 1)
        return crc == ord(data[2])
