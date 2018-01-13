#!/usr/bin/env python
""" Run this off the command line by:
sudo -HE env PATH=$PATH ./door_lock.py
"""

# *** TODO: This file does not get checked in to master. ***

import sys
from mpsse import *
from binascii import hexlify
import time

####################### NOTES ON HOW DOOR LOCK(S) WORK ###############################
# 1) The door locks are controlled by a I2C GPIO chip (MCP23017 and MCP23008), the MCP23008 is only on the octolock board
#       http://ww1.microchip.com/downloads/en/DeviceDoc/20001952C.pdf
#       http://ww1.microchip.com/downloads/en/DeviceDoc/21919e.pdf
# 2) At start up the control line latch bit must be initalized to 1 and not touched afterwards.  The latch register determines the value (high or low)
#    when that line is set to an output
# 2) Swtiching the control line is done by setting the IO directions register to input (unlocks) or output (locks handle). This will write the value set in
#    latch register to port bit.

# TODO: NEED TO TEST WITH OCOTOLOCK WHEN BOARD IS BUILT

# GPIO Chip addresses (resides on card edge and Octolock)
# Note since the caredge and octolock are on separate busses no need to worry about same addresses
WRITE_23017 = '\x42'
READ_23017 = '\x43'
WRITE_23008 = '\x40'
READ_23008 = '\x41'

# The octolock board is connected to channel 3
PCA9546WriteAddress = "\xE2"
PCA9546ReadAddress = "\xE3"

# Construct I2C switch channel 3
channel_3 = PCA9546WriteAddress + "\x08"

# Here are the bit locations associated with the lock signals
# Door Lock GPIO assignments

# CardEdge
# GPA0 - MLS3
# GPA1 - ELS3
# GPA2 - CONTROL3
# GPA3 - MLS4
# GPA4 - ELS4
# GPA5 - CONTROL4
# GPA6 - NC
# GPA7 - NC

# GPB0 - CONTROL2
# GPB1 - ELS2
# GPB2 - MLS2
# GPB3 - CONTROL1
# GPB4 - ELS1
# GPB5 - MLS1
# GPB6 - NC
# GPB7 - NC

# Expansion
# MCP23017
# GPA0 - CONTROL5
# GPA1 - CONTROL6
# GPA2 - CONTROL7
# GPA3 - CONTROL8
# GPA4 - CONTROL9
# GPA5 - CONTROL10
# GPA6 - CONTROL11
# GPA7 - CONTROL12

# GPB0 - ELS5
# GPB1 - ELS6
# GPB2 - ELS7
# GPB3 - ELS8
# GPB4 - ELS9
# GPB5 - ELS10
# GPB6 - ELS11
# GPB7 - ELS12

# MCP23008
# GP0 - MLS5
# GP1 - ELS6
# GP2 - ELS7
# GP3 - ELS8
# GP4 - ELS9
# GP5 - ELS10
# GP6 - ELS11
# GP7 - ELS12

# Control line, ELS, MLS bit masks
CONTROL1 = 0x08
CONTROL2 = 0x01
CONTROL3 = 0x04
CONTROL4 = 0x20
CONTROL5 = 0x01
CONTROL6 = 0x02
CONTROL7 = 0x04
CONTROL8 = 0x08
CONTROL9 = 0x10
CONTROL10 = 0x20
CONTROL11 = 0x40
CONTROL12 = 0x80

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

# Latch Register values for CardEdge and Octolock
LATCHA_CE = '\x24'
LATCHB_CE = '\x09'
LATCH_OCTO = '\xFF'

# The MCP23017 registers of use
OLATA_23017 = '\x14'
OLATB_23017 = '\x15'
IODIRA_23017 = '\x00'
IODIRB_23017 = '\x01'
GPIOA_23017 = '\x12'
GPIOB_23017 = '\x13'
IODIR_23008 = '\x00'
GPIO_23008 = '\x09'
OLAT_23008 = '\x0A'


# Start of Functions

def LockStatus(lock):
    elec_status = CheckELS()
    mech_status = CheckMLS()

    # Combine MLS and ELS into a 2 bit number
    # Bit 0 = ELS
    # Bit 1 = MLS
    # ELS can be shifted down by lock numer - 1
    elec_status >>= (lock - 1);

    # MLS is a little more tricky, lock one has to shifted up by 1
    # Lock 2 gets no shift
    # Lock > 2 gets shifted down by lock number - 2
    if lock == 1:
        mech_status <<= 1

    elif lock > 2:
        mech_status >>= (lock - 2)

    # Mask out the other bit and combine into status pointer
    elec_status &= 0x0001;
    mech_status &= 0x0002;

    status = mech_status | elec_status

    # The result of the 2 bit value is:
    # 3 0b11 -> ELS and MLS Inactive door secure
    # 2 0b10 -> ELS Inactive, MLS Active; door unlock by key
    # 1 0b01 -> ELS Active, MLS Inactive; door unlock by electrical
    # 0 0b00 -> ELS Active, MLS Active; door handle not fully secured

    return (status & 0xFF)


def CheckELS():
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

    # convert io_b into an interger for use
    io_b = ord(io_b)

    # shift down ELS1 to bit 0
    bit = (io_b & ELS1) >> 4;

    # store in els
    els = bit;

    # ELS2 is already at bit location 1
    bit = (io_b & ELS2);

    # store in els
    els = els | bit;

    # Point to Port A I/O register
    gpio.Start()
    gpio.Write(WRITE_23017 + GPIOA_23017)
    gpio.Stop()

    # Read out regiser
    gpio.Start()
    gpio.Write(READ_23017)
    gpio.SendNacks()
    io_a = gpio.Read(1)
    gpio.Stop()
    gpio.SendAcks()

    # Convert io_a into interger for use
    io_a = ord(io_a)

    # shift up ELS3 to bit 3
    bit = (io_a & ELS3) << 1;

    # store in els
    els = els | bit;

    # shit down ELS4 to bit location 4
    bit = (io_a & ELS4) >> 1;

    # store in els
    els = els | bit;

    # now read out ELS 5 -12 from the expansion board
    # need to set the switch to channel 3 first on the PCA9546A
    vec.Start()
    vec.Write(channel_3)
    vec.Stop()

    # All the ELS lines are connected to the MCP23017 B port
    # read out the GPIO B register
    vec.Start()
    vec.Write(WRITE_23017 + GPIOB_23017)
    vec.Stop()

    # Read out Port B
    vec.Start()
    vec.Write(READ_23017)
    vec.SendNacks()
    io_b = vec.Read(1)
    vec.Stop()
    vec.SendAcks()

    # convert io_b into an interger for use
    io_b = ord(io_b)

    # Shift the entire byte up by 4 so to pack it
    # with locks 1 - 4
    bit = (io_b << 4);

    els = els | bit;

    els &= 0xFF
    print 'Returned els: {}'.format(els)
    # return (els & 0xFF)
    return els


def CheckMLS():
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

    # convert io_b into an interger for use
    io_b = ord(io_b)

    # shitf down MLS1 to bit 0
    bit = (io_b & MLS1) >> 5;

    # store in MLS
    mls = bit;

    # shift down MLS2 to bit 1
    bit = (io_b & MLS2) >> 1;

    # store in MLS
    mls = mls | bit;

    # Point to Port A I/O register
    gpio.Start()
    gpio.Write(WRITE_23017 + GPIOA_23017)
    gpio.Stop()

    # Read out regiser
    gpio.Start()
    gpio.Write(READ_23017)
    gpio.SendNacks()
    io_a = gpio.Read(1)
    gpio.Stop()
    gpio.SendAcks()

    # Convert io_a into interger for use
    io_a = ord(io_a)

    # shift up MLS3 to bit 2
    bit = (io_a & MLS3) << 2;

    # store in MLS
    mls = mls | bit;

    # MLS4 is alreay in bit 3 so no need to shift
    mls = mls | (io_a & MLS4);

    # now read out MLS 5-12 from the expansion board
    # need to set the PCA9546A to channel 3 first
    vec.Start()
    vec.Write(channel_3)
    vec.Stop()

    # All the MLS lines are connected to the MCP23008
    vec.Start()
    vec.Write(WRITE_23008 + GPIO_23008)
    vec.Stop()

    # Read out the port
    vec.Start()
    vec.Write(READ_23008)
    vec.SendNacks()
    io = vec.Read(1)
    vec.Stop()
    vec.SendAcks()

    # convert io into an interger for use
    io = ord(io)

    # Shift the entire byte up by 4 so to pack it
    # with locks 1 - 4
    bit = (io << 4)

    mls = mls | bit

    mls &= 0xFF
    print 'Returned mls: {}'.format(mls)
    # return (mls & 0xFF)
    return mls


def Lock(lock):
    # Assign the correct durection register and mask associated with the door lock number
    if lock == 1:
        mask = CONTROL1
        dir_reg = IODIRB_23017

    elif lock == 2:
        mask = CONTROL2;
        dir_reg = IODIRB_23017

    elif lock == 3:
        mask = CONTROL3;
        dir_reg = IODIRA_23017

    elif lock == 4:
        mask = CONTROL4;
        dir_reg = IODIRA_23017

    elif lock == 5:
        mask = CONTROL5;
        dir_reg = IODIRA_23017

    elif lock == 6:
        mask = CONTROL6;
        dir_reg = IODIRA_23017

    elif lock == 7:
        mask = CONTROL7;
        dir_reg = IODIRA_23017

    elif lock == 8:
        mask = CONTROL8;
        dir_reg = IODIRA_23017

    elif lock == 9:
        mask = CONTROL9;
        dir_reg = IODIRA_23017

    elif lock == 10:
        mask = CONTROL10;
        dir_reg = IODIRA_23017

    elif lock == 11:
        mask = CONTROL11;
        dir_reg = IODIRA_23017

    elif lock == 12:
        mask = CONTROL12;
        latch = IODIRA_23017

    else:
        mask = 0x00;
        dir_reg = IODIRA_23017

    # first read out the direction register of the desired direction regiser of the MCP23017 (either CE or Octolock) as not to disturb
    # any of the other bits when the control line is set or cleared
    # if locks 1 - 4 then on cardedge the remaining on octolock
    if lock < 5:
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

        # This will set the IO bit connected to the Control line back to an input which will pull the line low and lock the door
        direction_int = direction_int | mask

        # now write that value into IO Direction
        gpio.Start()
        gpio.Write(WRITE_23017 + dir_reg + chr(direction_int))
        gpio.Stop()

        # ALL THE REMAINING LINES IN THIS FUNCTION ARE FOR DEBUG PURPOSES AND CAN BE REMOVED, READ OUT THE IO DIRECTION REGISTER TO VERIFY CONTENTS
        gpio.Start()
        gpio.Write(WRITE_23017 + dir_reg)
        gpio.Stop()
        gpio.Start()
        gpio.Write(READ_23017)
        gpio.SendNacks()
        direction = gpio.Read(1)
        gpio.Stop()
        gpio.SendAcks()
        print 'MCP23017 IO Direction Register: 0x%0.2X' % ord(direction)
    else:
        # Octolock
        # need to set the PCA9546A to channel 3 first
        vec.Start()
        vec.Write(channel_3)
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

        # This will set the IO bit connected to the Control line back to an input which will pull the line low and lock the door
        direction_int = direction_int | mask

        # now write that value into IO Direction
        vec.Start()
        vec.Write(WRITE_23017 + dir_reg + chr(direction_int))
        vec.Stop()

        # ALL THE REMAINING LINES IN THIS FUNCTION ARE FOR DEBUG PURPOSES AND CAN BE REMOVED, READ OUT THE IO DIRECTION REGISTER TO VERIFY CONTENTS
        vec.Start()
        vec.Write(WRITE_23017 + dir_reg)
        vec.Stop()
        vec.Start()
        vec.Write(READ_23017)
        vec.SendNacks()
        direction = vec.Read(1)
        vec.Stop()
        vec.SendAcks()
        print 'MCP23017 IO Direction Register: 0x%0.2X' % ord(direction)


def UnLock(lock):
    # Assign the correct registers and masks associated with the door lock number
    if lock == 1:
        mask = ~CONTROL1
        dir_reg = IODIRB_23017

    elif lock == 2:
        mask = ~CONTROL2;
        dir_reg = IODIRB_23017

    elif lock == 3:
        mask = ~CONTROL3;
        dir_reg = IODIRA_23017

    elif lock == 4:
        mask = ~CONTROL4;
        dir_reg = IODIRA_23017

    elif lock == 5:
        mask = ~CONTROL5;
        dir_reg = IODIRA_23017

    elif lock == 6:
        mask = ~CONTROL6;
        dir_reg = IODIRA_23017

    elif lock == 7:
        mask = ~CONTROL7;
        dir_reg = IODIRA_23017

    elif lock == 8:
        mask = ~CONTROL8;
        dir_reg = IODIRA_23017

    elif lock == 9:
        mask = ~CONTROL9;
        dir_reg = IODIRA_23017

    elif lock == 10:
        mask = ~CONTROL10;
        dir_reg = IODIRA_23017

    elif lock == 11:
        mask = ~CONTROL11;
        dir_reg = IODIRA_23017

    elif lock == 12:
        mask = ~CONTROL12;
        latch = IODIRA_23017

    else:
        mask = 0x00;
        dir_reg = IODIRA_23017

    # first read out the direction register of the port of interest of the MCP23017 so as not to disturb
    # any of the other bits when the control line is set or cleared
    # TODO: Need to set the approriate stuff for Octolock when it's reading to test!!
    # if locks 1 - 4 then on cardedge the remaining on octolock
    if lock < 5:
        gpio.Start()
        gpio.Write(WRITE_23017 + dir_reg)
        gpio.Stop()
        gpio.Start()
        gpio.Write(READ_23017)
        gpio.SendNacks()
        direction = gpio.Read(1)
        gpio.Stop()
        gpio.SendAcks()

        # convert directin to int
        direction_int = ord(direction)

        print direction_int

        # we need to set the IO line connected to the control to an output so it
        # pulls the control line high and unlocks the door (this set latch value to the port bit)
        direction_int = direction_int & (mask & 0xFF)

        print direction_int

        # now write that value into IO Direction
        gpio.Start()
        gpio.Write(WRITE_23017 + dir_reg + chr(direction_int))
        gpio.Stop()

        # ALL THE REMAINING LINES IN THIS FUNCTION ARE FOR DEBUG PURPOSES AND CAN BE REMOVED, READ OUT THE IO DIRECTION REGISTER TO VERIFY CONTENTS
        gpio.Start()
        gpio.Write(WRITE_23017 + dir_reg)
        gpio.Stop()
        gpio.Start()
        gpio.Write(READ_23017)
        gpio.SendNacks()
        direction = gpio.Read(1)
        gpio.Stop()
        gpio.SendAcks()
        print 'MCP23017 IO Direction Register: 0x%0.2X' % ord(direction)
    else:
        # Octolock
        # need to set the PCA9546A to channel 3 first
        vec.Start()
        vec.Write(channel_3)
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

        # convert directin to int
        direction_int = ord(direction)

        print direction_int

        # we need to set the IO line connected to the control to an output so it
        # pulls the control line high and unlocks the door (this set latch value to the port bit)
        direction_int = direction_int & (mask & 0xFF)

        print direction_int

        # now write that value into IO Direction
        vec.Start()
        vec.Write(WRITE_23017 + dir_reg + chr(direction_int))
        vec.Stop()

        # ALL THE REMAINING LINES IN THIS FUNCTION ARE FOR DEBUG PURPOSES AND CAN BE REMOVED, READ OUT THE IO DIRECTION REGISTER TO VERIFY CONTENTS
        vec.Start()
        vec.Write(WRITE_23017 + dir_reg)
        vec.Stop()
        vec.Start()
        vec.Write(READ_23017)
        vec.SendNacks()
        direction = vec.Read(1)
        vec.Stop()
        vec.SendAcks()
        print 'MCP23017 IO Direction Register: 0x%0.2X' % ord(direction)


def MomUnLock(lock):
    # Make it simple call the ulock function then wait the required 50ms to lock it again
    # This will cause to door lock to remain unlocked for 3 seconds before locking again
    UnLock(lock)

    # wait the required 50ms for a momentary unlock
    # after trial an error setting to 70ms in python works, 50ms must be too fast
    time.sleep(0.070)

    Lock(lock)


# GLOBALS
vec = MPSSE()
gpio = MPSSE()


def main():

    # Port A I2C for PCA9546A and gpio reset lines
    # vec = MPSSE()
    vec.Open(0x0403, 0x6011, I2C, ONE_HUNDRED_KHZ, MSB, IFACE_A)

    # Port B I2C for debug leds (don't need the io expander for the DPS sensors)
    # gpio = MPSSE()
    gpio.Open(0x0403, 0x6011, I2C, ONE_HUNDRED_KHZ, MSB, IFACE_B)

    # Set RESET line on PCA9546A to high to activate switch
    vec.PinHigh(GPIOL0)

    # Make sure reset line is held high on MCP23017 in order to use it
    vec.PinHigh(GPIOL2)

    time.sleep(0.005)
    # Since the control line has a pull up resistor we want to only set it low to active and use the
    # pull up to make it inactive.  To do this we need to use the IO direction register in the actual
    # setting of low and high (pull line low or leave in high impeadance which uses the pull up resistor)

    # In order to use the IO direction register we must set associated latch register to 1 so when the IO direction is
    # set to an output it will cause the IO pin connected to the control line to go high

    # Set Port A and B latches on CE
    gpio.Start()
    gpio.Write(WRITE_23017 + OLATA_23017 + LATCHA_CE)
    gpio.Stop()

    # Set Port B latches
    gpio.Start()
    gpio.Write(WRITE_23017 + OLATB_23017 + LATCHB_CE)
    gpio.Stop()

    # Set Port A latches on expansion
    # need to set the PCA9546A to channel 3 first
    vec.Start()
    vec.Write(channel_3)
    vec.Stop()

    vec.Start()
    vec.Write(WRITE_23017 + OLATA_23017 + LATCH_OCTO)
    vec.Stop()

    while 1:
        print "\r\n***** CEC Modbus Test *****"
        print "1 - Read Lock Status"
        print "2 - Lock Door"
        print "3 - Unlock Door"
        print "4 - Momentary Unlock"
        print "\r\nE - Exit Script"

        selection = raw_input("\r\nEnter Selection: ")

        if selection == '1':
            number = raw_input("\r\nEnter Door Number 1-12: ")
            door = int(number)

            status = LockStatus(door)
            print 'ELS and MLS Status Value: 0x%0.2X\n' % status
            if status == 3:
                print "Door Lock Secure"
            elif status == 2:
                print "MLS Active - Door Unlocked by Key. TODO: Believe this means Electrically Unlocked."
            elif status == 1:
                print "ELS Active - Door Electrically Unlocked. TODO: Believe this means Mechanically Unlocked."
            elif status == 0:
                print "ELS and MLS Active - Door Handle Not Secured"

        elif selection == '2':
            number = raw_input("\r\nEnter Door Number 1-12: ")
            door = int(number)
            Lock(door)

        elif selection == '3':
            number = raw_input("\r\nEnter Door Number 1-12: ")
            door = int(number)
            UnLock(door)

        elif selection == '4':
            number = raw_input("\r\nEnter Door Number 1-12: ")
            door = int(number)
            MomUnLock(door)

        elif selection == 'e' or selection == 'E':
            #  close serial port and I2C port
            vec.Close()
            gpio.Close()
            sys.exit()
        else:
            print "\r\nInvalid Selection!"


if __name__ == '__main__':
    main()

# gpio.Start()
# pio.Write("\x40")
# if gpio.GetAck() == ACK:
#    print "got ack"
#    gpio.Start()
#    gpio.Write("\x40\x01\x00")
#    gpio.Stop()
#    gpio.Start()
#    gpio.Write("\x40\x15\xFF")
#    gpio.Stop()
# else:
#    print "no ack"
# gpio.Close()
# vec.Close()
