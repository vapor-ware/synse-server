#!/usr/bin/env python
""" Synse RS485 Device Module

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

# We need to import these classes in order to initialize them so that
# get_all_subclasses() finds them. Without them, device registration will fail.
from synse.devicebus.devices.rs485.f660_airflow import F660Airflow
from synse.devicebus.devices.rs485.gs3_2010_fan_controller import GS32010Fan
from synse.devicebus.devices.rs485.rs485_device import RS485Device
from synse.devicebus.devices.rs485.sht31_humidity import SHT31Humidity
from synse.devicebus.devices.rs485.ecblue_fan_controller import ECblueFan
