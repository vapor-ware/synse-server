#!/usr/bin/env python
""" OpenDCRE Southbound Devicebus Interfaces

    Author: Erick Daniszewski
    Date:   09/15/2016

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
from i2c.i2c_device import I2CDevice
from plc.plc_device import PLCDevice
from redfish.redfish_device import RedfishDevice
from rs485.rs485_device import RS485Device
from ipmi.ipmi_device import IPMIDevice
from snmp.snmp_device import SnmpDevice

