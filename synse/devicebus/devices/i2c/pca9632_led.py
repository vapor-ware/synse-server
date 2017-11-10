#!/usr/bin/env python
""" Synse I2C LED control via PCA9632.

    Author: Andrew Cencini
    Date:   10/25/2016

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
import os
import sys

import lockfile

import synse.strings as _s_
from synse import constants as const
from synse.devicebus.constants import CommandId as cid
from synse.devicebus.devices.i2c.i2c_device import I2CDevice
from synse.devicebus.devices.i2c.pca9632_emulator import (read_emulator,
                                                          write_emulator)
from synse.devicebus.response import Response
from synse.errors import SynseException
from synse.protocols.i2c_common import i2c_common


logger = logging.getLogger(__name__)

PCA9632_WRITE = chr(0xC4)
PCA9632_READ = chr(0xC5)
PCA9632_LEDOUT_BLINK = chr(0x3F)
PCA9632_LEDOUT_STEADY = chr(0x2A)
PCA9632_LEDOUT_OFF = chr(0x00)
PCA9632_GRPPWM_FULL = chr(0xFC)
PCA9632_GRPFREQ_1S_BLINK = chr(0x17)

# register options
PCA9632_AUTO_INCR = chr(0x80)

# register map
PCA9632_MODE1 = chr(0x00)
PCA9632_MODE2 = chr(0x01)
PCA9632_PWM0 = chr(0x02)
PCA9632_PWM1 = chr(0x03)
PCA9632_PWM2 = chr(0x04)
PCA9632_PWM3 = chr(0x05)
PCA9632_GRPPWM = chr(0x06)
PCA9632_GRPFREQ = chr(0x07)
PCA9632_LEDOUT = chr(0x08)


class PCA9632Led(I2CDevice):
    """ Device subclass for LED via PCA9632 I2C.
    """
    _instance_name = 'pca-9632'

    def __init__(self, **kwargs):
        super(PCA9632Led, self).__init__(**kwargs)

        # Sensor specific commands.
        # TODO: Is this correct? Is there a read URL for leds?
        # It does not appear in the Synse 1.3 docs as a supported device type here:
        # https://docs.google.com/document/d/1HDbBjgkhJGTwEFD2fHycDDyUKt5ijWvgpOcLmQis4dk/edit#heading=h.atvexos4wq8q
        # Motion to deprecate the read led url in 2.0. (In a future commit.)
        self._command_map[cid.READ] = self._read
        self._command_map[cid.CHAMBER_LED] = self._chamber_led
        self._command_map[cid.LED] = self._read

        self._lock = lockfile.LockFile(self.serial_lock)

        self.channel = int(kwargs['channel'], 16)

        self.board_id = int(kwargs['board_offset']) + int(kwargs['board_id_range'][0])

        self.board_record = dict()
        self.board_record['board_id'] = format(self.board_id, '08x')
        self.board_record['devices'] = [
            {
                'device_id': kwargs['device_id'],
                'device_type': 'vapor_led',
                'device_info': kwargs.get('device_info', 'LED Controller')
            }
        ]

        # Cache last settings to avoid null responses on led power off.
        self.last_color = '000000'  # This should always be stored as a string. color may be an int.
        self.last_blink = 'steady'  # Do not store no_override here, just steady and blink.

    # TODO: This method gets called on both reads and writes. See the command map.
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
        led_state = command.data.get(_s_.LED_STATE)
        color = command.data.get(_s_.LED_COLOR)
        if color is not None:
            color = int(color, 16)
        blink = command.data.get(_s_.LED_BLINK)

        # normalize the device_type_string - if it's of 'led-type', make it
        # vapor_led for board/device matching later otherwise, leave it
        # alone, which will reject erroneous reads
        device_type_string = command.data.get(
            _s_.DEVICE_TYPE_STRING, const.DEVICE_VAPOR_LED
        )

        if device_type_string in [const.DEVICE_LED, const.DEVICE_VAPOR_LED]:
            device_type_string = const.DEVICE_VAPOR_LED

        try:
            # validate device to ensure device id and type are ok
            self._get_device_by_id(device_id, device_type_string)

            reading = self._control_led(
                state=led_state,
                color=color,
                blink=blink
            )

            if reading is not None:
                return Response(
                    command=command,
                    response_data=reading
                )

            # If we get here, there was no sensor device found, so we
            # must raise.
            logger.error('No response for LED status for command: {}'.format(
                command.data))
            raise SynseException('No LED status returned from I2C.')

        except Exception:
            logger.exception()
            raise SynseException(
                # NOTE: Writes go through this code path. Always did.
                'Error reading LED status (device id: {})'.format(
                    device_id)), None, sys.exc_info()[2]

    def _chamber_led(self, command):
        """ Chamber LED control command.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the chamber LED response.
        """
        # get the command data out from the incoming command
        device_id = command.data[_s_.DEVICE_ID]
        device_type_string = command.data[_s_.DEVICE_TYPE_STRING]

        try:
            # validate device to ensure device id and type are ok
            self._get_device_by_id(device_id, device_type_string)

            led_color = int(command.data[_s_.LED_COLOR], 16)

            reading = self._control_led(
                state=command.data[_s_.LED_STATE],
                blink=command.data[_s_.LED_BLINK_STATE],
                color=led_color
            )

            if reading is not None:
                return Response(
                    command=command,
                    response_data=reading
                )

            # If we get here, there was no sensor device found, so we
            # must raise.
            logger.error('No response for LED control for command: {}'.format(
                command.data))
            raise SynseException('No LED control response from I2C.')

        except Exception:
            logger.exception()
            raise SynseException(
                'Error setting LED status (device id: {})'.format(
                    device_id)), None, sys.exc_info()[2]

    def _led_response(self, state, color, blink):
        """Return an LED response dictionary with the given parameters with
        slight modifications.
        :param state: The LED state, on or off.
        :param color: The three byte hex RGB color of the LED.
            Example 0xff0000.
        :param blink: The blink state to return. steady or blink.
        :returns: The parameters in a dictionary with values as strings."""
        led_response = dict()
        led_response['led_state'] = state

        # color could be an int (write) or string (read). We need to return a string.
        if color is None:
            led_response['led_color'] = self.last_color
        else:
            if isinstance(color, int):
                led_response['led_color'] = '{:06x}'.format(color)
            else:
                led_response['led_color'] = color

        # Returning no_override is not worthwhile. Return the last setting we have.
        if blink is None or blink == 'no_override':
            led_response['blink_state'] = self.last_blink
        else:
            led_response['blink_state'] = blink
        return led_response

    def _control_led(self, state=None, blink=None, color=None):

        """ Internal method for LED control.

        Args:
            state (str): the LED state. can be either 'on' or 'off'.
            blink (str): the LED blink state. can be either 'steady' or 'blink'.
            color (str (emulator) str or int (production)):
                The 3 byte RGB color to set the LED to.

        Returns:
            dict: a dictionary containing the LED state, which includes its
                color, state, and blink state.
        """
        logger.debug('_control_led(): state {}, blink {}, color {}.'.format(state, blink, color))
        with self._lock:
            if self.hardware_type == 'emulator':
                # -- EMULATOR --> test-only code path
                if state is not None:
                    red = color >> 16
                    green = (color >> 8) & 0xff
                    blue = color & 0xff
                    write_emulator(self.device_name, self.channel,
                                   (red << 16) | (green << 8) | blue, state, blink)

                reading = read_emulator(self.device_name, self.channel)
                return {
                    _s_.LED_COLOR: format(reading['color'], '06x'),
                    _s_.LED_STATE: reading['state'],
                    _s_.LED_BLINK_STATE: reading['blink']
                }
            elif self.hardware_type == 'production':
                if state is None and blink is None and color is None:
                    return self._read_sensor()
                elif state is not None:
                    return self._write_sensor(state, color, blink)
                else:
                    logger.error('_control_led() Not read or write.')
                    raise SynseException(
                        'Unexpected arguments state: {}, color: {}, blink {}.'.format(
                            state, color, blink))
            else:
                raise SynseException('Unknown hardware_type {}.'.format(self.hardware_type))

    def _write_sensor(self, state, color, blink):
        """Write to the led controller either directly or indirectly.
        :param state: The LED state, on or off.
        :param color: The three byte hex RGB color of the LED.
            Example 0xff0000.
        :param blink: The blink state to return. steady or blink.
        :returns: The parameters in a dictionary with values as strings."""
        # We need to explicitly set the blink state internally in order to enable the LED output.
        if blink == 'no_override':
            blink = self.last_blink

        if self.from_background:
            return self._indirect_write(state, color, blink)
        else:
            return self.direct_write(state, color, blink)

    def _cache_write(self, color, blink):
        """Cache data written on a write.
        :param color: The three byte hex RGB color of the LED.
            Example 0xff0000.
        :param blink: The blink state to cache. steady or blink."""
        if color is not None:
            # color can be an int or a string. Cache as string.
            if isinstance(color, int):
                self.last_color = '{:06x}'.format(color)
            else:
                self.last_color = color
        if blink is not None and blink != 'no_override':
            self.last_blink = blink

    def direct_write(self, state, color, blink):
        """Direct write to the led controller.
        :param state: The LED state, on or off.
        :param color: The three byte hex RGB color of the LED.
            Example 0xff0000.
        :param blink: The blink state to return. steady or blink.
        :returns: The parameters in a dictionary with values as strings."""
        i2c_common.write_led(state=state, blink_state=blink, color=color)
        self._cache_write(color, blink)
        return self._led_response(state, color, blink)

    def _indirect_write(self, state, color, blink):
        """Write to a file that the daemon will read and send to the LED
        controller.
        :param state: The LED state, on or off.
        :param color: The three byte hex RGB color of the LED.
            Example 0xff0000.
        :param blink: The blink state to return. steady or blink.
        :returns: The parameters in a dictionary with values as strings."""
        logger.debug('indirect_sensor_write')
        i2c_common.check_led_write_parameters(state, color, blink)

        data_file = self._get_bg_write_file('{:04x}'.format(self.channel))

        if color is None:
            color_str = ''
        else:
            color_str = '{:06x}'.format(color)

        if blink is None:
            blink_str = ''
        else:
            blink_str = str(blink)

        write_data = state + os.linesep + color_str + os.linesep + blink_str + os.linesep
        logger.debug('LED _indirect_write() write_data: {}'.format(write_data))

        PCA9632Led.write_device_data_file(data_file, write_data)

        self._cache_write(color, blink)
        return self._led_response(state, color, blink)

    def _read_sensor(self):
        """Read from the LED controller either directly or indirectly.
        :returns: A dictionary of state, color and blink."""
        if self.from_background:
            return self._indirect_read()
        return self.direct_read()

    def direct_read(self):
        """Direct read of the LED controller.
        :returns: A dictionary of state, color and blink."""
        state, color, blink = i2c_common.read_led()
        return self._led_response(state, color, blink)

    def _indirect_read(self):
        """Read from a file created by a daemon.
        :returns: A dictionary of state, color and blink."""
        logger.debug('indirect_sensor_read')
        data_file = self._get_bg_read_file('{:04x}'.format(self.channel))
        data = PCA9632Led.read_sensor_data_file(data_file)
        return self._led_response(data[0], data[1], data[2])  # state, color, blink are data 0,1,2.
