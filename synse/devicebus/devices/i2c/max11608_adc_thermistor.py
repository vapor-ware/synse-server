#!/usr/bin/env python
""" Synse I2C thermistor via MAX11608 ADC

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
import sys
import time
import lockfile
from binascii import hexlify

from i2c_device import I2CDevice
from max11608_adc_emulator import read_emulator
import synse.strings as _s_
from synse import constants as const
from synse.devicebus.constants import CommandId as cid
from synse.devicebus.response import Response
from synse.errors import SynseException

from mpsse import *

logger = logging.getLogger(__name__)

# values used for slope intercept equation for temperature linear fit
# temperature = slope(ADC_VALUE - X1) + Y1
# From spreadsheet Brian Elect Thermistor Plot MAX11608.xlxs
slope = [-0.07073, -0.07525, -0.10448, -0.15029, -0.23762, -0.37143, -0.5]
X1 = [658, 398, 258, 168, 115, 78, 57]
Y1 = [18, 38, 53, 67, 80, 94, 105]

MAX_11608_WRITE_ADDRESS = 0x66
MAX_11608_READ_ADDRESS = 0x67
MAX_11608_SETUP_BYTE = 0xD2
MAX_11608_CONFIG_BYTE = 0x61


class Max11608Thermistor(I2CDevice):
    """ Device subclass for thermistor via MAX11608 I2C ADC.
    """
    _instance_name = 'max-11608'

    def __init__(self, **kwargs):
        super(Max11608Thermistor, self).__init__(**kwargs)

        # Sensor specific commands.
        self._command_map[cid.READ] = self._read

        self._lock = lockfile.LockFile(self.serial_lock)

        self.channel = int(kwargs['channel'], 16)

        self.board_id = int(kwargs['board_offset']) + int(kwargs['board_id_range'][0])

        self.board_record = dict()
        self.board_record['board_id'] = format(self.board_id, '08x')
        self.board_record['devices'] = [
            {
                'device_id': kwargs['device_id'],
                'device_type': 'temperature',
                'device_info': kwargs.get('device_info', 'CEC temperature')
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
            raise SynseException('Error reading temperature sensor (device id {})'.format(device_id)), None, sys.exc_info()[2]

    def _read_sensor(self):
        """

        Returns:

        """
        with self._lock:
            if self.hardware_type == 'emulator':
                # -- EMULATOR --> test-only code path
                return {const.UOM_TEMPERATURE: self._convert_reading(read_emulator(self.device_name, self.channel))}
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

                        # Set channel to 3 for MAX11608
                        vec.Start()
                        vec.Write('\xE2\x08')
                        vec.Stop()

                        # verify channel was set
                        vec.Start()
                        vec.Write('\xE3')
                        vec.SendNacks()
                        reg = vec.Read(1)
                        vec.Stop()
                        # FIXME: check disabled due to LED controller presence returning 0x00 when 0x08 is desired
                        """if ord(reg) != 0x08:
                            raise SynseException(
                                'Invalid data returned configuring I2C for thermistor read. ({})'.format(ord(reg)))"""

                        # Configure MAX11608: There are two registers to write to however there is no address.
                        # Bit 7 determines which register gets written; 0 = Configuration byte, 1 = Setup byte
                        vec.SendAcks()
                        vec.Start()

                        # Following the slave address write 0xD2 for setup byte and 0x0F for configuration byte
                        # See tables 1 and 2 in MAX11608 for byte definitions; set up for an internal reference
                        # and do an a/d conversion on given channel
                        vec.Write('' + chr(MAX_11608_WRITE_ADDRESS) + chr(MAX_11608_SETUP_BYTE) +
                                  chr(MAX_11608_CONFIG_BYTE + (self.channel << 1)))
                        if vec.GetAck() != ACK:
                            raise SynseException('I2C Bus Error: No ACK received after setup/configuration write.')

                        # Initiating a read starts the conversion
                        vec.Start()
                        vec.Write(chr(MAX_11608_READ_ADDRESS))

                        # delay for conversion since libmpsse can't do clock stretching
                        time.sleep(0.005)

                        # Read 1 channel (2 bytes per channel)
                        ad_reading = vec.Read(2)
                        vec.Stop()

                        # Combine the upper and lower byte into one string and convert to integer
                        ad_str = int(hexlify(ad_reading[0] + ad_reading), 16) & 0x03FF

                        return {const.UOM_TEMPERATURE: self._convert_reading(ad_str)}
                    else:
                        vec.Stop()
                        raise SynseException('I2C Bus Error: No ACK received on device initialization.')
                finally:
                    vec.Close()
                    gpio.Close()

    @staticmethod
    def _convert_reading(ad_str):
        # Calculate the Linear Fit temperature
        # Equations based on Brian Elect Thermistor Plot MAX11608.xlxs
        if ad_str >= X1[0]:
            # Region 7
            temperature = slope[0]*(ad_str - X1[0]) + Y1[0]
        elif (X1[0]-1) >= ad_str >= X1[1]:
            # Region 6
            temperature = slope[1]*(ad_str - X1[1]) + Y1[1]
        elif (X1[1]-1) >= ad_str >= X1[2]:
            # Region 5
            temperature = slope[2]*(ad_str - X1[2]) + Y1[2]
        elif (X1[2]-1) >= ad_str >= X1[3]:
            # Region 4
            temperature = slope[3]*(ad_str - X1[3]) + Y1[3]
        elif (X1[3]-1) >= ad_str >= X1[4]:
            # Region 3
            temperature = slope[4]*(ad_str - X1[4]) + Y1[4]
        elif (X1[4]-1) >= ad_str >= X1[5]:
            # Region 2
            temperature = slope[5]*(ad_str - X1[5]) + Y1[5]
        elif (X1[5]-1) >= ad_str >= X1[6]:
            # Region 1
            temperature = slope[6]*(ad_str - X1[6]) + Y1[6]
        else:
            # Hit max temperature of the thermistor
            temperature = 105.0
        return float('%0.3f' % temperature)
