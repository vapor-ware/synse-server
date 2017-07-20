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

# device names - these should match up with the device names defined
# in synse.
MAX_11608 = 'max-11608'  # i2c thermistor
PCA_9632 = 'pca-9632'  # i2c led
SDP_610 = 'sdp-610'  # i2c pressure
F660 = 'f660'  # rs485 airflow
GS3_2010 = 'gs3-2010'  # rs485 fan controller
SHT31 = 'sht31'  # rs485 humidity
