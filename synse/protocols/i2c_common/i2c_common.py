#!/usr/bin/env python
"""
        \\//
         \/apor IO


        Common file for i2c operations to avoid cut and paste.
        gs3 command line tool uses this code. This code will also be used
        under the devicebus.
"""

# pylint: disable=import-error
from mpsse import (ACK, GPIOL0, I2C, IFACE_A, IFACE_B, MPSSE, MSB,
                   ONE_HUNDRED_KHZ)

from binascii import hexlify
from mpsse import *
from ..conversions import conversions
import copy
import datetime
import logging
import struct
import time
from synse.stats import stats

logger = logging.getLogger(__name__)

# Proto 2 Board
# PCA9546A is a four channel I2C / SMBus switch.
PCA9546_WRITE_ADDRESS = '\xE2'
PCA9546_READ_ADDRESS = '\xE3'

# The number of times we read a differential pressure sensor in order to handle
# the turbulence that causes single reads to vary wildly.
DIFFERENTIAL_PRESSURE_READ_COUNT = 25


def _open_vec_i2c():
    """Open the i2c port on the VEC USB for i2c operations."""
    # Port A I2C for PCA9546A
    vec = MPSSE()
    vec.Open(0x0403, 0x6011, I2C, ONE_HUNDRED_KHZ, MSB, IFACE_A)

    # Port B I2C for debug leds (don't need the io expander for the DPS sensors)
    gpio = MPSSE()
    gpio.Open(0x0403, 0x6011, I2C, ONE_HUNDRED_KHZ, MSB, IFACE_B)

    # Set RESET line on PCA9546A to high to activate switch
    vec.PinHigh(GPIOL0)
    time.sleep(0.001)

    # Read channel of PCA9546A
    vec.Start()
    vec.Write(PCA9546_READ_ADDRESS)

    return vec, gpio


def _close_vec_i2c(vec, gpio):
    """Close the i2c port on the VEC USB."""
    vec.Stop()
    vec.Close()
    gpio.Close()


def _open_led_i2c():
    """Open the i2c port on the VEC USB for led controller operations."""
    # Construct string to set channel number to 3
    channel_str = PCA9546_WRITE_ADDRESS + '\x08'

    # Port A I2C for PCA9546A
    vec = MPSSE()
    vec.Open(0x0403, 0x6011, I2C, ONE_HUNDRED_KHZ, MSB, IFACE_A)

    # Port B I2C for debug leds (don't need the io expander for the LED Port)
    gpio = MPSSE()
    gpio.Open(0x0403, 0x6011, I2C, ONE_HUNDRED_KHZ, MSB, IFACE_B)

    # Set RESET line on PCA9546A to high to activate switch
    vec.PinHigh(GPIOL0)

    # Set channel on PCA9546A to 3 for PCA9632 (LED Port) Keep in mind this also is connected to the MAX11608
    vec.Start()
    vec.Write(channel_str)
    vec.Stop()

    # verify channel was set.
    vec.Start()
    vec.Write(PCA9546_READ_ADDRESS)
    vec.SendNacks()
    reg = vec.Read(1)
    vec.Stop()
    reg = ord(reg)
    if reg != 0x08:
        raise ValueError('Failed to set PCA9546A Control Register to 0x08. Is 0x{:02x}'.format(reg))

    vec.SendAcks()
    vec.Start()

    # Configure PCA9632 for our setup (IE totem pole with inverted driver output, etc)
    # Writes to Mode 1 and Mode 2 Registers
    vec.Start()
    vec.Write('\xC4\x80\x00\x35')
    vec.Stop()

    return vec, gpio


def _close_led_i2c(vec, gpio):
    """Close the i2c port on the VEC USB."""
    vec.Close()
    gpio.Close()


def get_channel_ordinal(channel):
    """The differential pressure sensors have a channel setting that uses a
    bit shift.
    :raises: ValueError on invalid channel."""
    channels = [1, 2, 4, 8, 16, 32, 64, 128]
    return channels.index(channel)


def get_channel_from_ordinal(ordinal):
    """The differential pressure sensors have a channel setting that uses a
    bit shift.
    :raises: ValueError on invalid channel."""
    channels = [1, 2, 4, 8, 16, 32, 64, 128]
    return channels[ordinal]


def _normalize_differential_pressure_result(channel, readings):
    """Normalize the raw differential pressure readings to produce a result.
    The raw readings will vary wildly due to turbulence.
    :param channel: The I2C channel of the sensor.
    :param readings: The raw differential pressure readings from the sensor.
    """
    # Dict for aggregating and logging.
    result_stats = {'sample_count': DIFFERENTIAL_PRESSURE_READ_COUNT}
    result_stats['raw_mean'], result_stats['raw_stddev'] = stats.std_dev(readings)

    # Remove outliers.
    readings_copy = copy.deepcopy(readings)
    outlier_results = stats.remove_outliers_percent(readings_copy, .3)

    # Get the results:
    result_stats['remove_count'] = outlier_results['removed']
    result_stats['outliers'] = outlier_results['outliers']
    result_stats['list'] = outlier_results['list']
    result_stats['mean'] = outlier_results['mean']
    result_stats['stddev'] = outlier_results['stddev']

    logger.debug('Differential Pressure Reading channel {}: result_stats{}'.format(
        channel, result_stats))

    return result_stats


def _read_differential_pressure_channel(vec, channel):
    """Internal common code for dp reads. This part handles the per channel bus
    reads.
    :param vec: Handle for reading.
    :param channel: The i2c channel to read.
    :returns: A list of differential pressure readings in Pascals. These will
    vary widely due to turbulence."""
    result = []

    # Set channel
    # Convert channel number to string and add to address.
    channel_str = PCA9546_WRITE_ADDRESS + chr(channel)

    vec.Start()
    vec.Write(channel_str)
    vec.Stop()

    # verify channel was set
    vec.Start()
    vec.Write(PCA9546_READ_ADDRESS)
    vec.SendNacks()

    channel_reading = vec.Read(1)
    channel_read = conversions.unpack_byte(channel_reading)
    if channel_read == channel:
        logger.debug('OK: Set differential pressure channel to {}'.format(channel_read))
    else:
        logger.error(
            'FAILED Setting differential pressure channel to {}, channel is {}'.format(
                channel, channel_read))

    vec.Stop()
    vec.SendAcks()

    # Read DP sensor connected to the set channel.
    for i in range(DIFFERENTIAL_PRESSURE_READ_COUNT):

        # Read DPS sensor connected to the set channel
        vec.SendAcks()
        vec.Start()
        vec.Write('\x80\xF1')
        vec.Start()
        vec.Write('\x81')

        # Give DPS610 time for the conversion since clock stretching is not implemented
        # 5ms seems to work fine, if wonkyness happens may have to increase.
        # So far this seems fine for 9 bit resolution.
        time.sleep(0.001)

        # Read the three bytes out of the DPS sensor (two data bytes and crc)
        sensor_data = vec.Read(3)
        vec.Stop()

        if _crc8(sensor_data):
            result.append(conversions.differential_pressure_sdp610(sensor_data, 0))
        else:
            logger.error('CRC failure reading Differential Pressure')

    if len(result) == 0:
        logger.error('No differential pressure readings for channel {}'.format(channel))
        return None
    return result


def configure_differential_pressure(channel):
    """Configure the differential pressure sensor for 9 bit resolution. Default
    is 12. This needs to be done once per power up. For our case we call this
    on synse container startup.
    :param channel: The channel to configure."""
    logger.debug('Configuring Differential Pressure sensor on channel {}'.format(channel))

    # Port A I2C for PCA9546A
    vec = MPSSE()
    vec.Open(0x0403, 0x6011, I2C, ONE_HUNDRED_KHZ, MSB, IFACE_A)

    # Set RESET line on PCA9546A to high to activate switch
    vec.PinHigh(GPIOL0)
    time.sleep(0.001)

    channel_str = PCA9546_WRITE_ADDRESS + chr(channel)
    logger.debug('PCA9546_WRITE_ADDRESS is: {}'.format(hexlify(PCA9546_WRITE_ADDRESS)))
    logger.debug('channel_str is: {}'.format(hexlify(channel_str)))

    vec.Start()
    vec.Write(channel_str)
    vec.Stop()

    logger.debug('PCA9546_READ_ADDRESS is: {}'.format(hexlify(PCA9546_READ_ADDRESS)))

    # verify channel was set
    vec.Start()
    vec.Write(PCA9546_READ_ADDRESS)
    vec.SendNacks()
    reg = vec.Read(1)
    vec.Stop()
    vec.SendAcks()

    logger.debug('PCA9546A Control Register: 0x{:02x}'.format(ord(reg)))

    # Configure Sensor
    # In the application note for changing measurement resolution three things must be met.
    # 1. Read the advanced user register.
    # 2. Define the new register entry according to the desired resolution.
    # 3. Write the new value to the advanced register.
    vec.Start()
    vec.Write('\x80\xE5')
    vec.Start()
    vec.Write('\x81')

    # At this point the sensor needs to hold the master but the FT4232 doesn't do clock stretching.
    time.sleep(0.001)  # This stays at 1 ms regardless of sensor resolution.

    # Read the three bytes out of the DPS sensor (two data bytes and crc)
    sensor_data = vec.Read(3)
    logger.debug('Raw sensor_data: {}'.format(hexlify(sensor_data)))
    vec.Stop()

    # write new value for 9 bit resolution (0b000 for bits 9 - 11)
    if _crc8(sensor_data):

        # Hardcoded 9 bit sensor resolution.
        sensor_int = 0x7182

        msb = sensor_int >> 8
        lsb = sensor_int & 0xFF
        register_str = '\x80\xE4' + chr(msb) + chr(lsb)

        vec.Start()
        vec.Write(register_str)
        vec.Stop()
        logger.debug('Configured DP Sensor on channel {} for 9 bit resolution.'.format(channel))
        rc = 0
    else:
        logger.error('CRC failed configuring DP Sensor.')
        rc = 1

    vec.Stop()
    vec.Close()
    return rc


def read_differential_pressure(channel):
    """This will read a single differential pressure sensor from the
    CEC board.
    :param channel: The channel to read.
    :returns: The differential pressure in Pascals, or None on failure."""
    vec, gpio = _open_vec_i2c()

    readings = None
    if vec.GetAck() == ACK:
        # If we got an ack then switch is there.
        vec.SendNacks()
        vec.Read(1)
        vec.Stop()
        vec.SendAcks()

        readings = _read_differential_pressure_channel(vec, channel)

        channel_str = PCA9546_WRITE_ADDRESS + '\x00'
        vec.Start()
        vec.Write(channel_str)
        vec.Stop()

    else:
        logger.error('No ACK from PCA9546A')
        _close_vec_i2c(vec, gpio)
        return None

    _close_vec_i2c(vec, gpio)

    # Now that the bus is closed, normalize the results.
    normalized_result = _normalize_differential_pressure_result(channel, readings)
    return normalized_result['mean']


def read_differential_pressures(count):
    """This will read count number of differential pressure sensors from the
    CEC board.
    :param count: The number of differential pressure sensors to read.
    :returns: An array of differential pressure sensor readings in Pascals.
    The array index will be the same as the channel in the synse i2c sdp-610
    differential pressure sensor configuration. None is returned on failure."""

    start_time = datetime.datetime.now()
    vec, gpio = _open_vec_i2c()
    result = []
    raw_result = []

    if vec.GetAck() == ACK:
        # If we got an ack then switch is there.
        vec.SendNacks()
        vec.Read(1)
        vec.Stop()
        vec.SendAcks()

        # Cycle through the count number of sensors connected to each channel
        # on the PCA9546A.
        channel = 1
        for _ in range(count):
            raw_result.append(_read_differential_pressure_channel(vec, channel))
            # set the next channel
            channel <<= 1

        channel_str = PCA9546_WRITE_ADDRESS + '\x00'
        vec.Start()
        vec.Write(channel_str)
        vec.Stop()
    else:
        logger.error('No ACK from PCA9546A')
        _close_vec_i2c(vec, gpio)
        return None

    _close_vec_i2c(vec, gpio)

    # Now that the bus is closed, normalize the results.
    for index, raw in enumerate(raw_result):
        channel = get_channel_from_ordinal(index)
        normalized = _normalize_differential_pressure_result(channel, raw)
        result.append(normalized['mean'])

    end_time = datetime.datetime.now()
    logger.debug('Differential Pressure Read time: {} ms'.format(
        (end_time - start_time).total_seconds() * 1000))
    for reading in result:
        logger.debug('Differential Pressure Reading:   {} Pa'.format(reading))
    return result

# PCA9632 LED Controller constants.
PCA9632_WRITE = chr(0xC4)
PCA9632_READ = chr(0xC5)
PCA9632_LEDOUT_BLINK = chr(0x3F)        # Brightness controlled by PWMx register. Blinking controlled by GRPPWM register
PCA9632_LEDOUT_STEADY = chr(0x2A)       # Brightness controlled by PWMx register.
PCA9632_LEDOUT_OFF = chr(0x00)          # Led output off.
PCA9632_GRPPWM_FULL = chr(0xFC)         # 98.4 % group duty cycle. 64-step duty cycle resolution.
PCA9632_GRPFREQ_2S_BLINK = chr(0x2F)    # Blink all LEDs at 2 second frequency. (one second on, one second off)

# register options
PCA9632_AUTO_INCR = chr(0x80)   # Enables Auto-Increment, Mode register 1.

# register map
PCA9632_MODE1 = chr(0x00)   # Mode register 1
PCA9632_MODE2 = chr(0x01)   # Mode register 2
PCA9632_PWM0 = chr(0x02)    # brightness control LED0
PCA9632_PWM1 = chr(0x03)    # brightness control LED1
PCA9632_PWM2 = chr(0x04)    # brightness control LED2
PCA9632_PWM3 = chr(0x05)    # brightness control LED3 (Unused if I understand correctly.)
PCA9632_GRPPWM = chr(0x06)  # group duty cycle control
PCA9632_GRPFREQ = chr(0x07) # group frequency
PCA9632_LEDOUT = chr(0x08)  # LED output state


def read_led():
    """Read the led state from the led controller. There is one led controller
    per wedge.
    :returns: state, color, and blink
    state is on or off.
    color is a 3 byte RGB color.
    blink is blink or steady."""
    vec, gpio = _open_led_i2c()

    # Read out color. PWM0 register. (Register 2)
    vec.Start()
    # write, auto increment, start at PWM0 register.
    vec.Write(PCA9632_WRITE + chr(ord(PCA9632_AUTO_INCR) | ord(PCA9632_PWM0)))
    vec.Stop()

    vec.Start()
    vec.Write(PCA9632_READ)    # start a read
    color = vec.Read(2)  # read three bytes to read PWM0, PWM1, PWM2
    vec.SendNacks()
    c2 = vec.Read(1)
    color += c2
    vec.Stop()

    # Read out Register 0x08 (LEDOUT).
    vec.Start()
    vec.Write(PCA9632_WRITE + PCA9632_LEDOUT)
    vec.Stop()

    vec.Start()
    vec.Write(PCA9632_READ)    # start a read
    ledout = vec.Read(1)
    vec.Stop()

    _close_led_i2c(vec, gpio)

    ledout = ord(ledout)
    logger.debug('PCA9632 Register 0x08: 0x{:02x}'.format(ledout))
    ledout = chr(ledout)
    color = hexlify(color)

    # Convert state and blink from the LEDOUT state register.
    if ledout == PCA9632_LEDOUT_OFF:
        state = 'off'
        blink = 'steady'
    elif ledout == PCA9632_LEDOUT_STEADY:
        state = 'on'
        blink = 'steady'
    elif ledout == PCA9632_LEDOUT_BLINK:
        state = 'on'
        blink = 'blink'
    else:
        raise ValueError('Unknown LEDOUT state 0x{}.'.format(hexlify(ledout)))

    return state, color, blink


def check_led_write_parameters(state, color=None, blink_state=None):
    """Check parameter validity.
    :param state: on or off
    :param color: A 3 byte RGB color or hex string. None is fine for off.
    :param blink_state: blink, steady, or no_override. None is fine for off."""
    # Parameter checks.
    if state not in ['on', 'off']:
        raise ValueError('Invalid state parameter {}.'.format(state))
    if state == 'on' and (color is None or blink_state is None):
        raise ValueError('Color and blink_state must be specified when state is on.')
    if blink_state not in ['blink', 'steady', 'no_override', None]:
        raise ValueError('Invalid blink_state {}.'.format(blink_state))
    if color is not None and (color < 0 or color > 0xFFFFFF):
        raise ValueError('Color {:0x} out of range. 0 <= color < 0xFFFFFF'.format(color))
    elif color is not None and blink_state is None:
        raise ValueError('color is not None and blink_state is None')
    elif color is None and blink_state is not None:
        raise ValueError('color is None and blink_state is not None')


def write_led(state, color=None, blink_state=None):
    """Set the led state.
    :param state: on or off
    :param color: A 3 byte RGB color or hex string. None is fine for off.
    :param blink_state: blink, steady, or no_override. None is fine for off."""

    # If color is a string, assume hex and convert to int.
    if isinstance(color, basestring):
        color = int(color, 16)

    # Parameter checks.
    check_led_write_parameters(state, color, blink_state)

    vec, gpio = _open_led_i2c()

    if state == 'off':
        # Turn off all outputs with the LEDOUT register.
        vec.Start()
        vec.Write(PCA9632_WRITE + PCA9632_LEDOUT + PCA9632_LEDOUT_OFF)  # write, LEDOUT register, 0x00 for off.
        vec.Stop()
    else:
        # Set the colors.
        color_bytes = struct.pack('>L', color)  # Pack color to three bytes.
        color_bytes = color_bytes[1:]
        to_write = PCA9632_WRITE + chr(ord(PCA9632_AUTO_INCR) | ord(PCA9632_PWM0)) + color_bytes

        vec.Start()
        vec.Write(to_write)
        vec.Stop()

        # Set the blink state.
        if blink_state == 'steady':
            vec.Start()
            vec.Write(PCA9632_WRITE + PCA9632_LEDOUT + PCA9632_LEDOUT_STEADY)
            vec.Stop()
        elif blink_state == 'blink':
            vec.Start()
            # Set group period for 1 second and group duty cycle of 50% (controls the blinking)
            # This writes to registers 6 and 7 by setting the increment bit in the register (0x86)
            vec.Write(PCA9632_WRITE + chr(ord(PCA9632_AUTO_INCR) | ord(PCA9632_GRPPWM)) +
                      '\x80' + PCA9632_GRPFREQ_2S_BLINK)
            vec.Stop()

            # Set the output to enable the blinking.
            vec.Start()
            vec.Write(PCA9632_WRITE + PCA9632_LEDOUT + PCA9632_LEDOUT_BLINK)
            vec.Stop()

    _close_led_i2c(vec, gpio)


def _get_thermistor_registers(device_name):
    """Get the read and write registers for the max116xx A/D converter attached
    to a thermistor.
    :param device_name: max_11608 and max_11610 are supported.
    :returns: read_register, write_register.
    :raises ValueError if device_name is not supported"""
    if device_name == 'max_11610':
        read_register = '\x6B'
        write_register = '\x6A'
    elif device_name == 'max_11608':
        read_register = '\x67'
        write_register = '\x66'
    else:
        raise ValueError('Unknown device_name {}.'.format(device_name))

    return read_register, write_register


def read_thermistors(count, device_name):
    """This will read count number of thermistors from the CEC board.
    :param count: The number of thermistors to read.
    :param: device_name max_11608 and max_11610 are supported.
    :returns: An array of thermistor readings in degrees Celsius. The array
    index will be the same as the channel in the synse i2c max-11608 thermistor
    configuration."""
    read_register, write_register = _get_thermistor_registers(device_name)

    # construct channel 3 command based on address
    channel_3 = PCA9546_WRITE_ADDRESS + '\x08'

    vec, gpio = _open_vec_i2c()

    if vec.GetAck() == ACK:

        # if we got an ack then slave is there
        vec.SendNacks()
        vec.Read(1)

        vec.SendAcks()
        vec.Stop()

        # Set channel to 3 for MAX11608
        vec.Start()
        vec.Write(channel_3)
        vec.Stop()

        # verify channel was set
        vec.Start()
        vec.Write(PCA9546_READ_ADDRESS)
        vec.SendNacks()
        vec.Read(1)
        vec.Stop()

        # Configure MAX116xx
        # There are two registers to write to however there is no address.
        # Bit 7 determines which register gets written; 0 = Configuration byte,
        # 1 = Setup byte
        vec.SendAcks()
        vec.Start()

        # Following the slave address write 0xD2 for setup byte and 0x0F for configuration
        # byte. See tables 1 and 2 in MAX116xx for byte definitions but basically sets up
        # for an internal reference and do an a/d conversion all channels
        vec.Write(write_register + '\xD2\x0F')

        # Initiating a read starts the conversion
        vec.Start()
        vec.Write(read_register)

        # delay for conversion since the libmpsse can't do clock stretching
        time.sleep(0.010)

        # Read the count number of channels (2 bytes per channel)
        ad_reading = vec.Read(count * 2)

    else:
        logger.error('No ACK from thermistors.')
        _close_vec_i2c(vec, gpio)
        return None

    _close_vec_i2c(vec, gpio)

    # Convert the raw reading for each thermistor.
    result = []
    if ad_reading:
        for x in range(count):
            index = x * 2
            temperature = conversions.convert_thermistor_reading(
                ad_reading, index, device_name)
            result.append(temperature)

    return result


def _crc8(data):
    """CRC check on the packet.
    :returns: True on success, False on failure."""
    polynomial = 0x131
    crc = 0
    for x in range(len(data) - 1):
        crc ^= ord(data[x])
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ polynomial
            else:
                crc = (crc << 1)

    return crc == ord(data[2])
