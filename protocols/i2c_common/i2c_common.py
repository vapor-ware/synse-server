#!/usr/bin/env python
"""
        \\//
         \/apor IO


        Common file for i2c operations to avoid cut and paste.
        gs3 command line tool needs to avoid synse-server/synse/__init__.py
        as it brings in a lot of dependencies. This code will also be used
        under the devicebus.
"""

from mpsse import *
import conversions.conversions as conversions
import logging
import time

logger = logging.getLogger(__name__)

# Proto 2 Board
PCA9546_WRITE_ADDRESS = '\xE2'
PCA9546_READ_ADDRESS = '\xE3'


def _start_i2c():
    """Common code for starting i2c reads."""
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


def _stop_i2c(vec, gpio):
    """Common code for stopping i2c reads."""
    vec.Stop()
    vec.Close()
    gpio.Close()


def _read_differential_pressure_channel(vec, channel):
    """Internal common code for dp reads.
    :param vec: Handle for reading.
    :param channel: The i2c channel to read.
    :returns: The differntial pressure in Pascals on success, None on
    failure."""
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
    vec.Read(1)
    vec.Stop()

    # Read DPS sensor connected to the set channel
    vec.SendAcks()
    vec.Start()
    vec.Write('\x80\xF1')
    vec.Start()
    vec.Write('\x81')

    # Give DPS610 time for the conversion since clock stretching is not implemented
    # 5ms seems to work fine, if wonkyness happens may have to increase.
    # So far this seems fine.
    time.sleep(0.005)

    # Read the three bytes out of the DPS sensor (two data bytes and crc)
    sensor_data = vec.Read(3)
    vec.Stop()

    if _crc8(sensor_data):
        return conversions.differential_pressure_sdp610(sensor_data, 0)

    else:
        logger.error('CRC Failed')
        return None


def read_differential_pressure(channel):
    """This will a single differential pressure sensor from the
    CEC board.
    :param channel: The channel to read.
    :returns: The differential pressure in Pascals, or None on failure."""
    vec, gpio = _start_i2c()

    result = None
    if vec.GetAck() == ACK:
        # If we got an ack then switch is there.
        vec.SendNacks()
        vec.Read(1)
        vec.Stop()
        vec.SendAcks()

        result = _read_differential_pressure_channel(vec, channel)

        channel_str = PCA9546_WRITE_ADDRESS + '\x00'
        vec.Start()
        vec.Write(channel_str)
        vec.Stop()

    else:
        # If we can't get an ack, result will be an empty list.
        logger.error("No ACK from PCA9546A")

    _stop_i2c(vec, gpio)
    return result


def read_differential_pressures(count):
    """This will read count number of differential pressure sensors from the
    CEC board.
    :param count: The number of differential pressure sensors to read.
    :returns: An array of differential pressure sensor readings in Pascals.
    The array index will be the same as the channel in the synse i2c sdp-610
    differential pressure sensor configuration. None is returned on failure."""

    vec, gpio = _start_i2c()
    result = []

    if vec.GetAck() == ACK:
        # If we got an ack then switch is there.
        vec.SendNacks()
        vec.Read(1)
        vec.Stop()
        vec.SendAcks()

        # Cycle through the count number of sensors connected to each channel
        # on the PCA9546A.
        channel = 1
        for x in range(count):

            result.append(_read_differential_pressure_channel(vec, channel))
            # set the next channel
            channel = channel << 1

        channel_str = PCA9546_WRITE_ADDRESS + '\x00'
        vec.Start()
        vec.Write(channel_str)
        vec.Stop()
    else:
        # If we can't get an ack, result will be an empty list.
        logger.error("No ACK from PCA9546A")

    _stop_i2c(vec, gpio)
    return result


def read_thermistors(count):
    """This will read count number of thermistors from the CEC board.
    :param count: The number of thermistors to read.
    :returns: An array of thermistor readings in degrees Celsius. The array
    index will be the same as the channel in the synse i2c max-11608 thermistor
    configuration."""

    logger.debug('read_thermistors 1')

    # construct channel 3 command based on address
    channel_3 = PCA9546_WRITE_ADDRESS + '\x08'

    vec, gpio = _start_i2c()

    ad_reading = None
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

        # Configure MAX11608
        # There are two registers to write to however there is no address.
        # Bit 7 determines which register gets written; 0 = Configuration byte, 1 = Setup byte
        vec.SendAcks()
        vec.Start()

        # Following the slave address write 0xD2 for setup byte and 0x0F for configuration byte
        # See tables 1 and 2 in MAX11608 for byte definitions but basically sets up for an internal reference
        # and do an a/d conversion all channels
        vec.Write("\x66\xD2\x0F")

        # Initiating a read starts the conversion
        vec.Start()
        vec.Write("\x67")

        # delay for conversion since the libmpsse can't do clock stretching
        time.sleep(0.010)

        # Read the count number of channels (2 bytes per channel)
        ad_reading = vec.Read(count * 2)

    else:
        # If we can't get an ack, result will be an empty list. (see below)
        logger.error('No ACK from thermistors.')

    _stop_i2c(vec, gpio)

    # Convert the raw reading for each thermistor.
    result = []
    if ad_reading:
        for x in range(count):
            index = x * 2
            temperature = conversions.thermistor_max11608_adc(
                ad_reading[index:index + 2])
            result.append(temperature)

    return result


def _crc8(data):
    """CRC check on the packet.
    :returns: True on success, False on failure."""
    polynomial = 0x131
    crc = 0
    for x in range(len(data) - 1):
        crc ^= ord(data[x])
        for y in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ polynomial
            else:
                crc = (crc << 1)

    return crc == ord(data[2])
