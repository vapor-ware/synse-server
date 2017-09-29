#!/usr/bin/env python
""" Synse I2C Device Module

    Author: Erick Daniszewski
    Date:   05 May 2017

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
# pylint: skip-file

from synse.devicebus.devices.i2c.i2c_device import I2CDevice
from synse.devicebus.devices.i2c.pca9632_led import PCA9632Led
from synse.devicebus.devices.i2c.sdp610_pressure import SDP610Pressure
