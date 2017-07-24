#!/usr/bin/env python
""" Constant values used for SNMP.

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

# Emulator test measurement units.
# We expect these in the SNMP results. They are defined in the MIB.
EMULATOR_UNIT_UNDEFINED = 1
EMULATOR_UNIT_TEMPERATURE = 2
EMULATOR_UNIT_CURRENT = 3
EMULATOR_UNIT_POWER = 4
EMULATOR_UNIT_EFFECTIVE_POWER = 5
EMULATOR_UNIT_HUMIDITY = 6
EMULATOR_UNIT_VOLTAGE = 7
EMULATOR_UNIT_ENERGY = 8
EMULATOR_UNIT_FREQUENCY = 9
EMULATOR_UNIT_ACCESS = 10
EMULATOR_UNIT_LEAKAGE = 11
EMULATOR_UNIT_PERCENT = 12
EMULATOR_UNIT_RPM = 13
EMULATOR_UNIT_CO2 = 14
EMULATOR_UNIT_PUE = 15  # Power usage effectiveness
EMULATOR_UNIT_FLOW = 16
EMULATOR_UNIT_TIME = 17
EMULATOR_UNIT_COSTS = 18
EMULATOR_UNIT_IMP = 19  # TODO: Find out what this is. Some Imperial Unit?
EMULATOR_UNIT_HEAT_CAPACITY = 20
EMULATOR_UNIT_CONSTANT = 21
EMULATOR_UNIT_TEMPERATURE_DIFF = 22
# TODO: Will need formatting / examples here. This time span may not be a broad standard.
EMULATOR_UNIT_TIMESPAN = 23
EMULATOR_UNIT_CYCLES = 24

EMULATOR_UNIT_PULSE_RATE = 34
EMULATOR_UNIT_PRESSURE = 35
EMULATOR_UNIT_ACCELERATION = 36
EMULATOR_UNIT_TIMESPAN_TICKS = 37

# Need a map of the above to our device type strings.
EMULATOR_UNIT_TO_DEVICE_TYPE_MAP = {
    EMULATOR_UNIT_UNDEFINED: 'undefined',
    EMULATOR_UNIT_TEMPERATURE: 'temperature',
    EMULATOR_UNIT_CURRENT: 'current',
    EMULATOR_UNIT_POWER: 'power',
    EMULATOR_UNIT_EFFECTIVE_POWER: 'effective_power',
    EMULATOR_UNIT_HUMIDITY: 'humidity',
    EMULATOR_UNIT_VOLTAGE: 'voltage',
    EMULATOR_UNIT_ENERGY: 'energy',
    EMULATOR_UNIT_FREQUENCY: 'frequency',
    EMULATOR_UNIT_ACCESS: 'access',
    EMULATOR_UNIT_LEAKAGE: 'leakage',
    EMULATOR_UNIT_PERCENT: 'percent',
    # Hijacking this one for fan_speed. It may be that we have a one to many mapping in the future.
    EMULATOR_UNIT_RPM: 'fan_speed',  # MIB has rpm.
    EMULATOR_UNIT_CO2: 'co2',
    EMULATOR_UNIT_PUE: 'pue',
    EMULATOR_UNIT_FLOW: 'flow',
    EMULATOR_UNIT_TIME: 'time',  # TODO: Be careful with data format. Need a real walk for this.
    EMULATOR_UNIT_COSTS: 'costs',
    EMULATOR_UNIT_IMP: 'imp',
    EMULATOR_UNIT_HEAT_CAPACITY: 'heat_capacity',
    EMULATOR_UNIT_CONSTANT: 'constant',
    EMULATOR_UNIT_TEMPERATURE_DIFF: 'temperature_diff',
    EMULATOR_UNIT_CYCLES: 'cycles',
    EMULATOR_UNIT_PULSE_RATE: 'pulse_rate',
    EMULATOR_UNIT_PRESSURE: 'pressure',
    EMULATOR_UNIT_ACCELERATION: 'acceleration',
    EMULATOR_UNIT_TIMESPAN_TICKS: 'timespan_ticks',
}
