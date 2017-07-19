#!/usr/bin/env python
""" Constant values for background sensor read.

    Author: Erick Daniszewski
    Date:   18 July 2017

    \\//
     \/apor IO
"""

POLYNOMIAL1 = 0x131
POLYNOMIAL2 = 0xA001

MODBUS_SLAVE_ADDRESS = 0x02

# addresses for PCA9546A I2C switch
PCA9546_READ_ADDRESS = '\xE3'
PCA9546_WRITE_ADDRESS = '\xE2'
