#!/usr/bin/env python
"""
        \\//
         \/apor IO


        Common file for i2c operations to avoid cut and paste.
        gs3 command line tool uses this code. This code will also be used
        under the devicebus.
"""

# pylint: disable=import-error

from binascii import hexlify
import copy
import datetime
import logging
import struct
import time

from mpsse import (ACK, GPIOL0, GPIOL2, I2C, IFACE_A, IFACE_B, MPSSE,
                   MSB, ONE_HUNDRED_KHZ)

from synse.stats import stats
from ..conversions import conversions

logger = logging.getLogger(__name__)

# Proto 2 Board
# PCA9546A is a four channel I2C / SMBus switch.
PCA9546_WRITE_ADDRESS = '\xE2'
PCA9546_READ_ADDRESS = '\xE3'

# Construct I2C switch channel 3
CHANNEL3 = PCA9546_WRITE_ADDRESS + '\x08'

# The number of times we read a differential pressure sensor in order to handle
# the turbulence that causes single reads to vary wildly.
DIFFERENTIAL_PRESSURE_READ_COUNT = 25


# Masks for lock controls by lock number.
LOCK_CONTROL1 = 0x08
LOCK_CONTROL2 = 0x01
LOCK_CONTROL3 = 0x04
LOCK_CONTROL4 = 0x20
LOCK_CONTROL5 = 0x01
LOCK_CONTROL6 = 0x02
LOCK_CONTROL7 = 0x04
LOCK_CONTROL8 = 0x08
LOCK_CONTROL9 = 0x10
LOCK_CONTROL10 = 0x20
LOCK_CONTROL11 = 0x40
LOCK_CONTROL12 = 0x80

# Doing a quick lock control of the rev 1 hardware which only has one lock
# here are the bit locations associated with the lock signals
# Control line is on GPA7 (Port A bit 7) of the MCP23017
# ELS is on GPA6 (Port A bit 6) of the MCP23017
# MLS is on GPA5 (Port A bit 5) of the MCP23017
# Using this value for masking for the rev 1 board.
CONTROL = 0x80

# Electronic Lock Status by lock number.
ELS1 = 0x10
ELS2 = 0x02
ELS3 = 0x02
ELS4 = 0x10
ELS5 = 0x01
ELS6 = 0x02
ELS7 = 0x04
ELS8 = 0x08
ELS9 = 0x10
ELS10 = 0x20
ELS11 = 0x40
ELS12 = 0x80

# Mechanical Lock Status by lock number.
MLS1 = 0x20
MLS2 = 0x04
MLS3 = 0x01
MLS4 = 0x08
MLS5 = 0x01
MLS6 = 0x02
MLS7 = 0x04
MLS8 = 0x08
MLS9 = 0x10
MLS10 = 0x20
MLS11 = 0x40
MLS12 = 0x80

# GPIO expander addresses and registers
# Lock rev 2 hardware.
WRITE_23017 = '\x42'
READ_23017 = '\x43'
WRITE_23008 = '\x40'
READ_23008 = '\x41'
IODIRA_23017 = '\x00'
IODIRB_23017 = '\x01'
GPIOA_23017 = '\x12'
GPIOB_23017 = '\x13'
OLATA_23017 = '\x14'
OLATB_23017 = '\x15'
IODIR_23008 = '\x00'
GPIO_23008 = '\x09'
OLAT_23008 = '\x0A'

# I2C switch
WRITE_9546A = '\xE2'
READ_9546A = '\xE3'


# Latch Register values for CardEdge and Octolock
LATCHA_CE = '\x24'
LATCHB_CE = '\x09'
LATCH_OCTO = '\xFF'


# vec and gpio handles are opened once. We do not explicitly close them
# since we need to hold the reset line in order to unlock a lock.
# The underlying code does not appear to clean up the HID port when close is
# not explicitly called which in this case is good.
class VecHandles(object):
    """This class exposes handles to the HID responsible for I2C communication
    in the chamber."""
    class __VecHandles(object):
        """Internal class to facilitate opening the HID interface for I2c
        communication."""
        def __init__(self):
            logger.debug('Initializing __VecHandles')
            self.vec = MPSSE()
            logger.debug('opening vec')
            self.vec.Open(0x0403, 0x6011, I2C, ONE_HUNDRED_KHZ, MSB, IFACE_A)

            # Port B I2C for debug leds (don't need the io expander for the DPS sensors)
            self.gpio = MPSSE()
            logger.debug('opening gpio')
            self.gpio.Open(0x0403, 0x6011, I2C, ONE_HUNDRED_KHZ, MSB, IFACE_B)

            # Set RESET line on PCA9546A to high to activate switch
            logger.debug('GPIOL0 high')
            self.vec.PinHigh(GPIOL0)

            # Make sure reset line is held high on MCP23017 in order to use it
            logger.debug('GPIOL2 high')
            self.vec.PinHigh(GPIOL2)

            time.sleep(0.005)
            # Since the control line has a pull up resistor we want to only set it low to
            # active and use the pull up to make it inactive. To do this we need to use
            # the IO direction register in the actual setting of low and high (pull line
            # low or leave in high impedance which uses the pull up resistor)

            # In order to use the IO direction register we must set associated latch
            # register to 1 so when the IO direction is set to an output it will cause the
            # IO pin connected to the control line to go high

            # Set Port A and B latches on CE (card edge).
            self.gpio.Start()
            logger.debug('writing: {}'.format(hexlify(WRITE_23017 + OLATA_23017 + LATCHA_CE)))
            self.gpio.Write(WRITE_23017 + OLATA_23017 + LATCHA_CE)
            self.gpio.Stop()

            # Set Port B latches.
            self.gpio.Start()
            logger.debug('writing: {}'.format(hexlify(WRITE_23017 + OLATB_23017 + LATCHB_CE)))
            self.gpio.Write(WRITE_23017 + OLATB_23017 + LATCHB_CE)
            self.gpio.Stop()

            # Set Port A latches on expansion.
            # Need to set the PCA9546A to channel 3 first.
            self.vec.Start()
            logger.debug('writing: {}'.format(hexlify(CHANNEL3)))
            self.vec.Write(CHANNEL3)
            self.vec.Stop()

            self.vec.Start()
            logger.debug('writing: {}'.format(hexlify(WRITE_23017 + OLATA_23017 + LATCH_OCTO)))
            self.vec.Write(WRITE_23017 + OLATA_23017 + LATCH_OCTO)
            self.vec.Stop()

            logger.debug('vec and gpio initialized')

    instance = None

    def __init__(self):
        """Initializes the instance if it does not exist."""
        if not VecHandles.instance:
            VecHandles.instance = VecHandles.__VecHandles()


def _get_lock_parameters(lock_number, is_lock):
    """
    Gets the lock parameters to send out given the devices and the lock index.
    :param lock_number: Index of the lock to operate on (1-12).
    :param is_lock: True for lock, False for unlock.
    :return: mask, direction register.
    :raises ValueError: Invalid parameter.
    """

    # Assign the correct direction register and mask associated with the door lock number
    if lock_number == 1:
        mask = LOCK_CONTROL1
        dir_reg = IODIRB_23017

    elif lock_number == 2:
        mask = LOCK_CONTROL2
        dir_reg = IODIRB_23017

    elif lock_number == 3:
        mask = LOCK_CONTROL3
        dir_reg = IODIRA_23017

    elif lock_number == 4:
        mask = LOCK_CONTROL4
        dir_reg = IODIRA_23017

    elif lock_number == 5:
        mask = LOCK_CONTROL5
        dir_reg = IODIRA_23017

    elif lock_number == 6:
        mask = LOCK_CONTROL6
        dir_reg = IODIRA_23017

    elif lock_number == 7:
        mask = LOCK_CONTROL7
        dir_reg = IODIRA_23017

    elif lock_number == 8:
        mask = LOCK_CONTROL8
        dir_reg = IODIRA_23017

    elif lock_number == 9:
        mask = LOCK_CONTROL9
        dir_reg = IODIRA_23017

    elif lock_number == 10:
        mask = LOCK_CONTROL10
        dir_reg = IODIRA_23017

    elif lock_number == 11:
        mask = LOCK_CONTROL11
        dir_reg = IODIRA_23017

    elif lock_number == 12:
        mask = LOCK_CONTROL12
        dir_reg = IODIRA_23017

    else:
        raise ValueError('Invalid lock number {}. 1-12 are supported.'.format(lock_number))

    # Invert the mask on unlock.
    if not is_lock:
        mask = ~mask

    logger.debug('mask: {:02x}, dir_reg: {}.'.format(mask, hexlify(dir_reg)))
    return mask, dir_reg


def lock_lock(lock_number):
    """
    Lock a lock by index (1-12)
    :param lock_number: The index of the lock to lock.
    """
    logger.debug('Locking lock {}'.format(lock_number))

    # Get the mask and direction register. Get the vec and gpio handles.
    mask, dir_reg = _get_lock_parameters(lock_number, True)
    vec = VecHandles().instance.vec
    gpio = VecHandles().instance.gpio

    # First read out the direction register of the desired direction register
    # of the MCP23017 (either CE or Octolock) as not to disturb
    # any of the other bits when the control line is set or cleared
    # if locks 1 - 4 then on card edge the remaining on octolock
    if lock_number < 5:
        gpio.Start()
        gpio.Write(WRITE_23017 + dir_reg)
        gpio.Stop()
        gpio.Start()
        gpio.Write(READ_23017)
        gpio.SendNacks()
        direction = gpio.Read(1)
        gpio.Stop()
        gpio.SendAcks()

        # convert direction to int
        direction_int = ord(direction)

        # This will set the IO bit connected to the Control line back to an
        # input which will pull the line low and lock the door
        direction_int = direction_int | mask

        # now write that value into IO Direction
        gpio.Start()
        gpio.Write(WRITE_23017 + dir_reg + chr(direction_int))
        gpio.Stop()

        # ALL THE REMAINING LINES IN THIS FUNCTION ARE FOR DEBUG PURPOSES AND
        # CAN BE REMOVED, READ OUT THE IO DIRECTION REGISTER TO VERIFY CONTENTS
        gpio.Start()
        gpio.Write(WRITE_23017 + dir_reg)
        gpio.Stop()
        gpio.Start()
        gpio.Write(READ_23017)
        gpio.SendNacks()
        direction = gpio.Read(1)
        gpio.Stop()
        gpio.SendAcks()
        logger.debug('MCP23017 IO Direction Register: 0x%0.2X', ord(direction))
    else:
        # Octolock
        # need to set the PCA9546A to channel 3 first
        vec.Start()
        vec.Write(CHANNEL3)
        vec.Stop()

        # Point the direction register and read out
        vec.Start()
        vec.Write(WRITE_23017 + dir_reg)
        vec.Stop()
        vec.Start()
        vec.Write(READ_23017)
        vec.SendNacks()
        direction = vec.Read(1)
        vec.Stop()
        vec.SendAcks()

        # convert direction to int
        direction_int = ord(direction)

        # This will set the IO bit connected to the Control line back to an
        # input which will pull the line low and lock the door
        direction_int = direction_int | mask

        # now write that value into IO Direction
        vec.Start()
        vec.Write(WRITE_23017 + dir_reg + chr(direction_int))
        vec.Stop()

        # ALL THE REMAINING LINES IN THIS FUNCTION ARE FOR DEBUG PURPOSES AND
        # CAN BE REMOVED, READ OUT THE IO DIRECTION REGISTER TO VERIFY CONTENTS
        vec.Start()
        vec.Write(WRITE_23017 + dir_reg)
        vec.Stop()
        vec.Start()
        vec.Write(READ_23017)
        vec.SendNacks()
        direction = vec.Read(1)
        vec.Stop()
        vec.SendAcks()
        logger.debug('MCP23017 IO Direction Register: 0x%0.2X', ord(direction))


def lock_momentary_unlock(lock_number):
    """
    Momentarily unlock a lock (for about 3 seconds).
    :param lock_number: The index of the lock to lock.
    """
    logger.debug('Momentary unlock lock {}'.format(lock_number))

    # Make it simple call the unlock function then wait the required 50ms to lock it again
    # This will cause to door lock to remain unlocked for 3 seconds before locking again
    lock_unlock(lock_number)

    # Wait the required time for a momentary unlock.
    # After trial an error setting to 70ms in python works, 50ms must be too fast.
    time.sleep(0.070)

    lock_lock(lock_number)


def check_els():
    """
    Check the electrical status of all locks 1-12.
    :return: The electrical status of all locks. Inactive (1) means locked,
    Active (0) means unlocked. Bit 0 is lock 1. Bit 11 is lock 12.
    """
    logger.debug('check_els()')

    vec = VecHandles().instance.vec
    gpio = VecHandles().instance.gpio

    # Point to the Port B I/O register on CE
    gpio.Start()
    logger.debug('writing: {}'.format(hexlify(WRITE_23017 + GPIOB_23017)))
    gpio.Write(WRITE_23017 + GPIOB_23017)
    gpio.Stop()

    # read out register
    gpio.Start()
    gpio.Write(READ_23017)
    logger.debug('writing: {}'.format(hexlify(READ_23017)))
    gpio.SendNacks()
    io_b = gpio.Read(1)
    logger.debug('read: {}'.format(hexlify(io_b)))
    gpio.Stop()
    gpio.SendAcks()

    # convert io_b into an integer for use
    io_b = ord(io_b)

    # shift down ELS1 to bit 0
    bit = (io_b & ELS1) >> 4

    # store in els
    els = bit

    # ELS2 is already at bit location 1
    bit = io_b & ELS2

    # store in els
    els |= bit

    # Point to Port A I/O register
    gpio.Start()
    logger.debug('writing: {}'.format(hexlify(WRITE_23017 + GPIOB_23017)))
    gpio.Write(WRITE_23017 + GPIOA_23017)
    gpio.Stop()

    # Read out register
    gpio.Start()
    logger.debug('writing: {}'.format(hexlify(READ_23017)))
    gpio.Write(READ_23017)
    gpio.SendNacks()
    io_a = gpio.Read(1)
    logger.debug('read: {}'.format(hexlify(io_a)))
    gpio.Stop()
    gpio.SendAcks()

    # Convert io_a into integer for use
    io_a = ord(io_a)

    # shift up ELS3 to bit 3
    bit = (io_a & ELS3) << 1

    # store in els
    els |= bit

    # shift down ELS4 to bit location 4
    bit = (io_a & ELS4) >> 1

    # store in els
    els |= bit

    # now read out ELS 5 -12 from the expansion board
    # need to set the switch to channel 3 first on the PCA9546A
    vec.Start()
    logger.debug('writing: {}'.format(hexlify(CHANNEL3)))
    vec.Write(CHANNEL3)
    vec.Stop()

    # All the ELS lines are connected to the MCP23017 B port
    # read out the GPIO B register
    vec.Start()
    logger.debug('writing: {}'.format(hexlify(WRITE_23017 + GPIOB_23017)))
    vec.Write(WRITE_23017 + GPIOB_23017)
    vec.Stop()

    # Read out Port B
    vec.Start()
    vec.Write(READ_23017)
    vec.SendNacks()
    io_b = vec.Read(1)
    logger.debug('read: {}'.format(hexlify(io_b)))
    vec.Stop()
    vec.SendAcks()

    # convert io_b into an integer for use
    io_b = ord(io_b)

    # Shift the entire byte up by 4 so to pack it
    # with locks 1 - 4
    bit = (io_b << 4)

    els |= bit

    return els & 0xFF


def check_mls():
    """
    Check the mechanical status of all locks 1-12.
    :return: The mechanical status of all locks. Inactive (1) means locked,
    Active (0) means unlocked. Bit 0 is lock 1. Bit 11 is lock 12.
    """
    vec = VecHandles().instance.vec
    gpio = VecHandles().instance.gpio

    # Point to the Port B I/O register on CE
    gpio.Start()
    gpio.Write(WRITE_23017 + GPIOB_23017)
    gpio.Stop()

    # read out register
    gpio.Start()
    gpio.Write(READ_23017)
    gpio.SendNacks()
    io_b = gpio.Read(1)
    gpio.Stop()
    gpio.SendAcks()

    # convert io_b into an integer for use
    io_b = ord(io_b)

    # shift down MLS1 to bit 0
    bit = (io_b & MLS1) >> 5

    # store in MLS
    mls = bit

    # shift down MLS2 to bit 1
    bit = (io_b & MLS2) >> 1

    # store in MLS
    mls |= bit

    # Point to Port A I/O register
    gpio.Start()
    gpio.Write(WRITE_23017 + GPIOA_23017)
    gpio.Stop()

    # Read out register
    gpio.Start()
    gpio.Write(READ_23017)
    gpio.SendNacks()
    io_a = gpio.Read(1)
    gpio.Stop()
    gpio.SendAcks()

    # Convert io_a into integer for use
    io_a = ord(io_a)

    # shift up MLS3 to bit 2
    bit = (io_a & MLS3) << 2

    # store in MLS
    mls |= bit

    # MLS4 is alreay in bit 3 so no need to shift
    mls |= io_a & MLS4

    # now read out MLS 5-12 from the expansion board
    # need to set the PCA9546A to channel 3 first
    vec.Start()
    vec.Write(CHANNEL3)
    vec.Stop()

    # All the MLS lines are connected to the MCP23008
    vec.Start()
    vec.Write(WRITE_23008 + GPIO_23008)
    vec.Stop()

    # Read out the port
    vec.Start()
    vec.Write(READ_23008)
    vec.SendNacks()
    reading = vec.Read(1)
    vec.Stop()
    vec.SendAcks()

    # convert io into an integer for use
    reading = ord(reading)

    # Shift the entire byte up by 4 so to pack it
    # with locks 1 - 4
    bit = reading << 4

    mls |= bit

    return mls & 0xFF


def lock_status(lock_number):
    """
    Get the status of a lock.
    :param lock_number: Lock 1-12
    :return:
    0 = ELS and MLS Active - Door Handle Not Secured.
    1 = ELS Active - Door Electrically Unlocked.
    2 = MLS Active - Door Unlocked by Key.
    3 = Door Lock Secure.
    """
    logger.debug('lock status, lock_number: {}'.format(lock_number))
    elec_status = check_els()
    logger.debug('elec_status: 0x{:02x}'.format(elec_status))
    mech_status = check_mls()
    logger.debug('mech_status: 0x{:02x}'.format(mech_status))

    # Combine MLS and ELS into a 2 bit number
    # Bit 0 = ELS
    # Bit 1 = MLS
    # ELS can be shifted down by lock number - 1
    elec_status >>= (lock_number - 1)

    # MLS is a little more tricky, lock one has to shifted up by 1
    # Lock 2 gets no shift
    # Lock > 2 gets shifted down by lock number - 2
    if lock_number == 1:
        mech_status <<= 1

    elif lock_number > 2:
        mech_status >>= (lock_number - 2)

    # Mask out the other bit and combine into status pointer
    elec_status &= 0x0001
    mech_status &= 0x0002

    status = mech_status | elec_status
    return status & 0xFF


def lock_unlock(lock_number):
    """
    Unlock a lock by index (1-12)
    :param lock_number: The index of the lock to lock.
    """
    logger.debug('Unlocking lock {}'.format(lock_number))

    # Get the mask and direction register. Get the vec and gpio handles.
    mask, dir_reg = _get_lock_parameters(lock_number, False)
    vec = VecHandles().instance.vec
    gpio = VecHandles().instance.gpio

    # First read out the direction register of the port of interest of the
    # MCP23017 so as not to disturb any of the other bits when the control line
    # is set or cleared
    # TODO: Need to set the approriate stuff for Octolock when it's reading to
    # test!! if locks 1 - 4 then on cardedge the remaining on octolock
    if lock_number < 5:
        gpio.Start()
        gpio.Write(WRITE_23017 + dir_reg)
        gpio.Stop()
        gpio.Start()
        gpio.Write(READ_23017)
        gpio.SendNacks()
        direction = gpio.Read(1)
        gpio.Stop()
        gpio.SendAcks()

        # convert direction to int
        direction_int = ord(direction)

        logger.debug(direction_int)

        # we need to set the IO line connected to the control to an output so it
        # pulls the control line high and unlocks the door (this set latch value
        # to the port bit)
        direction_int = direction_int & (mask & 0xFF)

        logger.debug(direction_int)

        # now write that value into IO Direction
        gpio.Start()
        gpio.Write(WRITE_23017 + dir_reg + chr(direction_int))
        gpio.Stop()

        # ALL THE REMAINING LINES IN THIS FUNCTION ARE FOR DEBUG PURPOSES AND
        # CAN BE REMOVED, READ OUT THE IO DIRECTION REGISTER TO VERIFY CONTENTS
        gpio.Start()
        gpio.Write(WRITE_23017 + dir_reg)
        gpio.Stop()
        gpio.Start()
        gpio.Write(READ_23017)
        gpio.SendNacks()
        direction = gpio.Read(1)
        gpio.Stop()
        gpio.SendAcks()
        logger.debug('MCP23017 IO Direction Register: 0x%0.2X', ord(direction))
    else:
        # Octolock
        # need to set the PCA9546A to channel 3 first
        vec.Start()
        vec.Write(CHANNEL3)
        vec.Stop()

        # Read out the direction register
        vec.Start()
        vec.Write(WRITE_23017 + dir_reg)
        vec.Stop()
        vec.Start()
        vec.Write(READ_23017)
        vec.SendNacks()
        direction = vec.Read(1)
        vec.Stop()
        vec.SendAcks()

        # convert direction to int
        direction_int = ord(direction)

        logger.debug(direction_int)

        # we need to set the IO line connected to the control to an output so it
        # pulls the control line high and unlocks the door (this set latch value
        # to the port bit)
        direction_int = direction_int & (mask & 0xFF)

        logger.debug(direction_int)

        # now write that value into IO Direction
        vec.Start()
        vec.Write(WRITE_23017 + dir_reg + chr(direction_int))
        vec.Stop()

        # ALL THE REMAINING LINES IN THIS FUNCTION ARE FOR DEBUG PURPOSES AND
        # CAN BE REMOVED, READ OUT THE IO DIRECTION REGISTER TO VERIFY CONTENTS
        vec.Start()
        vec.Write(WRITE_23017 + dir_reg)
        vec.Stop()
        vec.Start()
        vec.Write(READ_23017)
        vec.SendNacks()
        direction = vec.Read(1)
        vec.Stop()
        vec.SendAcks()
        logger.debug('MCP23017 IO Direction Register: 0x%0.2X', ord(direction))


def validate_lock_write_action(action):
    """
    Validate a lock action string for writes. Valid actions are lock, unlock,
    and momentary_unlock.
    :param action: The string to validate.
    :raises ValueError: Invalid action for a lock write.
    """
    if action not in ['lock', 'unlock', 'momentary_unlock']:
        raise ValueError('Invalid action provided for lock control.')


def _open_led_i2c():
    """Open the i2c port on the VEC USB for led controller operations.
    :returns: The vec handle to the HID device that speaks I2C to the LED
    controller."""
    vec = VecHandles().instance.vec

    # Construct string to set channel number to 3
    channel_str = PCA9546_WRITE_ADDRESS + '\x08'

    # Set channel on PCA9546A to 3 for PCA9632 (LED Port) Keep in mind this
    # also is connected to the MAX11608
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

    return vec


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

    if readings is None:
        # Bad sensor read. Don't fail the fan_sensors web route.
        result_stats['raw_mean'] = None
        result_stats['raw_stddev'] = None
        result_stats['remove_count'] = None
        result_stats['outliers'] = None
        result_stats['list'] = None
        result_stats['mean'] = None
        result_stats['stddev'] = None
        return result_stats

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
    for _ in range(DIFFERENTIAL_PRESSURE_READ_COUNT):

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
    vec = VecHandles().instance.vec

    # Read channel of PCA9546A
    vec.Start()
    vec.Write(PCA9546_READ_ADDRESS)

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
        vec.Stop()
        return None

    vec.Stop()

    # Now that the bus is closed, normalize the results.
    normalized_result = _normalize_differential_pressure_result(channel, readings)
    if normalized_result is None:
        return None  # Read of bad sensor.
    return normalized_result['mean']


def read_differential_pressures(count):
    """This will read count number of differential pressure sensors from the
    CEC board.
    :param count: The number of differential pressure sensors to read.
    :returns: An array of differential pressure sensor readings in Pascals.
    The array index will be the same as the channel in the synse i2c sdp-610
    differential pressure sensor configuration. None is returned on failure."""

    start_time = datetime.datetime.now()
    vec = VecHandles().instance.vec

    # Read channel of PCA9546A
    vec.Start()
    vec.Write(PCA9546_READ_ADDRESS)

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
        vec.Stop()
        return None

    vec.Stop()

    # Now that the bus is closed, normalize the results.
    for index, raw in enumerate(raw_result):
        channel = get_channel_from_ordinal(index)
        normalized = _normalize_differential_pressure_result(channel, raw)
        if normalized is None:
            return None  # Read of bad sensor.

        # Return the mean.
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

# Brightness controlled by PWMx register. Blinking controlled by GRPPWM register
PCA9632_LEDOUT_BLINK = chr(0x3F)
PCA9632_LEDOUT_STEADY = chr(0x2A)       # Brightness controlled by PWMx register.
PCA9632_LEDOUT_OFF = chr(0x00)          # Led output off.
PCA9632_GRPPWM_FULL = chr(0xFC)         # 98.4 % group duty cycle. 64-step duty cycle resolution.

# Blink all LEDs at 2 second frequency. (one second on, one second off)
PCA9632_GRPFREQ_2S_BLINK = chr(0x2F)

# register options
PCA9632_AUTO_INCR = chr(0x80)   # Enables Auto-Increment, Mode register 1.

# register map
PCA9632_MODE1 = chr(0x00)    # Mode register 1
PCA9632_MODE2 = chr(0x01)    # Mode register 2
PCA9632_PWM0 = chr(0x02)     # brightness control LED0
PCA9632_PWM1 = chr(0x03)     # brightness control LED1
PCA9632_PWM2 = chr(0x04)     # brightness control LED2
PCA9632_PWM3 = chr(0x05)     # brightness control LED3 (Unused if I understand correctly.)
PCA9632_GRPPWM = chr(0x06)   # group duty cycle control
PCA9632_GRPFREQ = chr(0x07)  # group frequency
PCA9632_LEDOUT = chr(0x08)   # LED output state


def read_led():
    """Read the led state from the led controller. There is one led controller
    per wedge.
    :returns: state, color, and blink
    state is on or off.
    color is a 3 byte RGB color.
    blink is blink or steady."""
    vec = _open_led_i2c()

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

    vec = _open_led_i2c()

    if state == 'off':
        # Turn off all outputs with the LEDOUT register.
        vec.Start()
        # write, LEDOUT register, 0x00 for off.
        vec.Write(PCA9632_WRITE + PCA9632_LEDOUT + PCA9632_LEDOUT_OFF)
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


def _get_thermistor_registers(device_name):
    """Get the read and write registers for the max116xx A/D converter attached
    to a thermistor.
    :param device_name: max-11608 and max-11610 are supported.
    :returns: read_register, write_register.
    :raises ValueError if device_name is not supported"""
    if device_name == 'max-11610':
        read_register = '\x6B'
        write_register = '\x6A'
    elif device_name == 'max-11608':
        read_register = '\x67'
        write_register = '\x66'
    else:
        raise ValueError('Unknown device_name {}.'.format(device_name))

    return read_register, write_register


def read_thermistors(count, device_name):
    """This will read count number of thermistors from the CEC board.
    :param count: The number of thermistors to read.
    :param device_name: max-11608 and max-11610 are supported.
    :returns: An array of thermistor readings in degrees Celsius. The array
    index will be the same as the channel in the synse i2c max-11608 thermistor
    configuration."""
    read_register, write_register = _get_thermistor_registers(device_name)

    # construct channel 3 command based on address
    channel_3 = PCA9546_WRITE_ADDRESS + '\x08'

    vec = VecHandles().instance.vec

    # Read channel of PCA9546A
    vec.Start()
    vec.Write(PCA9546_READ_ADDRESS)

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
        vec.Stop()
        return None

    vec.Stop()

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
