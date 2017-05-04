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
import lockfile
import sys

from i2c_device import I2CDevice
from pca9632_emulator import read_emulator, write_emulator
import synse.strings as _s_
from synse import constants as const
from synse.devicebus.constants import CommandId as cid
from synse.devicebus.response import Response
from synse.errors import SynseException

from mpsse import *

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
        blink = command.data.get(_s_.LED_BLINK)

        # normalize the device_type_string - if it's of 'led-type', make it vapor_led for board/device matching later
        # otherwise, leave it alone, which will reject erroneous reads
        device_type_string = command.data.get(_s_.DEVICE_TYPE_STRING, const.DEVICE_VAPOR_LED)
        if device_type_string in [const.DEVICE_LED, const.DEVICE_VAPOR_LED]:
            device_type_string = const.DEVICE_VAPOR_LED

        # if there is an on/off here, the color and blink must have been passed in - otherwise, just return LED status
        if led_state is not None and (color is None or blink is None):
            raise SynseException('Color and blink must be specified on Vapor LED {} commands.'.format(led_state))

        try:
            # validate device to ensure device id and type are ok
            self._get_device_by_id(device_id, device_type_string)

            reading = self._control_led()

            if reading is not None:
                return Response(
                    command=command,
                    response_data=reading
                )

            # if we get here, there was no sensor device found, so we must raise
            logger.error('No response for LED status for command: {}'.format(command.data))
            raise SynseException('No LED status returned from I2C.')

        except Exception:
            raise SynseException('Error reading LED status (device id: {})'.format(device_id)), None, sys.exc_info()[2]

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
                red=led_color >> 16,
                green=(led_color >> 8) & 0xff,
                blue=led_color & 0xff
            )

            if reading is not None:
                return Response(
                    command=command,
                    response_data=reading
                )

            # if we get here, there was no sensor device found, so we must raise
            logger.error('No response for LED control for command: {}'.format(command.data))
            raise SynseException('No LED control response from I2C.')

        except Exception:
            raise SynseException('Error setting LED status (device id: {})'.format(device_id)), None, sys.exc_info()[2]

    def _control_led(self, state=None, blink=None, red=None, green=None, blue=None):
        """ Internal method for LED control.

        Args:
            state (str): the LED state. can be either 'on' or 'off'.
            blink (str): the LED blink state. can be either 'steady' or 'blink'.
            red (int): the value for red (between 0x00 and 0xFF).
            green (int): the value for green (between 0x00 and 0xFF).
            blue (int): the value for blue (between 0x00 and 0xFF).

        Returns:
            dict: a dictionary containing the LED state, which includes its
                color, state, and blink state.
        """
        with self._lock:
            if self.hardware_type == 'emulator':
                # -- EMULATOR --> test-only code path
                if state is not None:
                    write_emulator(self.device_name, self.channel, (red << 16) | (green << 8) | blue, state, blink)
                reading = read_emulator(self.device_name, self.channel)
                return {
                    _s_.LED_COLOR: format(reading['color'], '06x'),
                    _s_.LED_STATE: reading['state'],
                    _s_.LED_BLINK_STATE: reading['blink']
                }
            else:
                # LED VEC LED ASSIGNMENTS
                # LED0/PWM0 = RED
                # LED1/PWM1 = GREEN
                # LED2/PWM2 = BLUE

                # Port A I2C for PCA9546A
                vec = MPSSE()
                vec.Open(0x0403, 0x6011, I2C, ONE_HUNDRED_KHZ, MSB, IFACE_A)

                # Port B I2C for debug leds (don't need the io expander for the LED Port)
                gpio = MPSSE()
                gpio.Open(0x0403, 0x6011, I2C, ONE_HUNDRED_KHZ, MSB, IFACE_B)

                try:
                    # Set RESET line on PCA9546A to high to activate switch
                    vec.PinHigh(GPIOL0)

                    # Set channel on PCA9546A to 3 for PCA9632 (LED Port)
                    # Keep in mind this also is connected to the MAX11608
                    vec.Start()
                    vec.Write('\xE2\x08')
                    vec.Stop()

                    # verify channel was set
                    vec.Start()
                    vec.Write('\xE3')
                    vec.SendNacks()
                    reg = vec.Read(1)
                    vec.Stop()
                    logger.debug('PCA9546A Control Register: 0x%0.2X' % ord(reg))

                    vec.SendAcks()
                    vec.Start()

                    # Configure PCA9632 for our setup (IE totem pole with inverted driver output, etc)
                    # Writes to Mode 1 and Mode 2 Registers
                    # 0x80 = 0b1000 0000 -> auto increment starting at 0
                    # write 0x00 to mode reg 1 => pca9632 does not respond to all-call
                    # write 0x35 to mode reg 2 => grp blink ctrl, external driver, change on stop, totem pole
                    vec.Start()
                    vec.Write(PCA9632_WRITE + chr(ord(PCA9632_AUTO_INCR) | ord(PCA9632_MODE1)) + '\x00\x35')
                    vec.Stop()

                    if state == _s_.LED_OFF:
                        # turn off all outputs via LEDOUT
                        vec.Start()
                        vec.Write(PCA9632_WRITE + PCA9632_LEDOUT + PCA9632_LEDOUT_OFF)
                        vec.Stop()
                    elif blink == _s_.LED_STEADY and state == _s_.LED_ON:
                        # set the LED colors via PWM
                        vec.Start()
                        vec.Write(PCA9632_WRITE + chr(ord(PCA9632_AUTO_INCR) | ord(PCA9632_PWM0)) + chr(red) +
                                  chr(green) + chr(blue))
                        vec.Stop()
                        vec.Start()
                        # then set the LEDOUT to steady and on
                        vec.Write(PCA9632_WRITE + PCA9632_LEDOUT + PCA9632_LEDOUT_STEADY)
                        vec.Stop()
                    elif blink == _s_.LED_BLINK and state == _s_.LED_ON:
                        # set the color of the LEDs to blink
                        vec.Start()
                        vec.Write(PCA9632_WRITE + chr(ord(PCA9632_AUTO_INCR) | ord(PCA9632_PWM0)) + chr(red) +
                                  chr(green) + chr(blue))
                        vec.Stop()
                        # now, set the group PWM to full power and a 1 second blink frequency - NB: this could be
                        # combined with the stuff below
                        vec.Start()
                        vec.Write(PCA9632_WRITE + chr(ord(PCA9632_AUTO_INCR) | ord(PCA9632_GRPPWM)) + '\x80' +
                                  PCA9632_GRPFREQ_1S_BLINK)
                        vec.Stop()
                        # finally, toggle the LEDOUT to use the blink settings set previously
                        vec.Start()
                        vec.Write(PCA9632_WRITE + PCA9632_LEDOUT + PCA9632_LEDOUT_BLINK)
                        vec.Stop()

                    # finally, read out the color settings and whether the leds are on / off or blinking
                    vec.Start()
                    vec.Write(PCA9632_WRITE + chr(ord(PCA9632_AUTO_INCR) | ord(PCA9632_PWM0)))
                    vec.Stop()
                    vec.Start()
                    vec.Write(PCA9632_READ)
                    color = vec.Read(2)
                    vec.SendNacks()
                    color += vec.Read(1)
                    vec.Stop()

                    # get state
                    vec.SendAcks()
                    vec.Start()
                    vec.Write(PCA9632_WRITE + PCA9632_LEDOUT)
                    vec.Stop()
                    vec.Start()
                    vec.Write(PCA9632_READ)
                    vec.SendNacks()
                    led_state = vec.Read(1)
                    vec.Stop()
                    vec.SendAcks()
                finally:
                    vec.Close()
                    gpio.Close()

                led_response = dict()
                if led_state == PCA9632_LEDOUT_OFF:
                    led_response['led_state'] = _s_.LED_OFF
                    led_response['blink_state'] = _s_.LED_STEADY
                elif led_state == PCA9632_LEDOUT_STEADY:
                    led_response['led_state'] = _s_.LED_ON
                    led_response['blink_state'] = _s_.LED_STEADY
                elif led_state == PCA9632_LEDOUT_BLINK:
                    led_response['led_state'] = _s_.LED_ON
                    led_response['blink_state'] = _s_.LED_BLINK
                else:
                    raise SynseException('Invalid LED State returned from LED controller: {}'.format(ord(led_state)))

                led_response['led_color'] = format(ord(color[2]) | (ord(color[1]) << 8) | (ord(color[0]) << 16), '06x')
                return led_response
