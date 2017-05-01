#!/usr/bin/env python
""" Constant values used for SNMP.

    \\//
     \/apor IO
"""

# Rittal RiZone measurement units.
# We expect these in the SNMP results. They are defined in the MIB.
RIZONE_UNIT_UNDEFINED = 1
RIZONE_UNIT_TEMPERATURE = 2
RIZONE_UNIT_CURRENT = 3
RIZONE_UNIT_POWER = 4
RIZONE_UNIT_EFFECTIVE_POWER = 5
RIZONE_UNIT_HUMIDITY = 6
RIZONE_UNIT_VOLTAGE = 7
RIZONE_UNIT_ENERGY = 8
RIZONE_UNIT_FREQUENCY = 9
RIZONE_UNIT_ACCESS = 10
RIZONE_UNIT_LEAKAGE = 11
RIZONE_UNIT_PERCENT = 12
RIZONE_UNIT_RPM = 13
RIZONE_UNIT_CO2 = 14
RIZONE_UNIT_PUE = 15  # Power usage effectiveness
RIZONE_UNIT_FLOW = 16
RIZONE_UNIT_TIME = 17
RIZONE_UNIT_COSTS = 18
RIZONE_UNIT_IMP = 19  # TODO: Find out what this is. Some Imperial Unit?
RIZONE_UNIT_HEAT_CAPACITY = 20
RIZONE_UNIT_CONSTANT = 21
RIZONE_UNIT_TEMPERATURE_DIFF = 22
RIZONE_UNIT_TIMESPAN = 23  # TODO: Will need formatting / examples here. This timespan may not be a broad standard.
RIZONE_UNIT_CYCLES = 24

RIZONE_UNIT_PULSE_RATE = 34
RIZONE_UNIT_PRESSURE = 35
RIZONE_UNIT_ACCELERATION = 36
RIZONE_UNIT_TIMESPAN_TICKS = 37

# Need a map of the above to our device type strings.
RIZONE_UNIT_TO_DEVICE_TYPE_MAP = {
    RIZONE_UNIT_UNDEFINED: "undefined",
    RIZONE_UNIT_TEMPERATURE: "temperature",
    RIZONE_UNIT_CURRENT: "current",
    RIZONE_UNIT_POWER: "power",
    RIZONE_UNIT_EFFECTIVE_POWER: "effective_power",
    RIZONE_UNIT_HUMIDITY: "humidity",
    RIZONE_UNIT_VOLTAGE: "voltage",
    RIZONE_UNIT_ENERGY: "energy",
    RIZONE_UNIT_FREQUENCY: "frequency",
    RIZONE_UNIT_ACCESS: "access",
    RIZONE_UNIT_LEAKAGE: "leakage",
    RIZONE_UNIT_PERCENT: "percent",
    # Hijacking this one for fan_speed. It may be that we have a one to many mapping in the future.
    RIZONE_UNIT_RPM: "fan_speed",  # MIB has rpm.
    RIZONE_UNIT_CO2: "co2",
    RIZONE_UNIT_PUE: "pue",
    RIZONE_UNIT_FLOW: "flow",
    RIZONE_UNIT_TIME: "time",  # TODO: Be careful with data format. Need a real walk for this.
    RIZONE_UNIT_COSTS: "costs",
    RIZONE_UNIT_IMP: "imp",
    RIZONE_UNIT_HEAT_CAPACITY: "heat_capacity",
    RIZONE_UNIT_CONSTANT: "constant",
    RIZONE_UNIT_TEMPERATURE_DIFF: "temperature_diff",
    RIZONE_UNIT_CYCLES: "cycles",
    RIZONE_UNIT_PULSE_RATE: "pulse_rate",
    RIZONE_UNIT_PRESSURE: "pressure",
    RIZONE_UNIT_ACCELERATION: "acceleration",
    RIZONE_UNIT_TIMESPAN_TICKS: "timespan_ticks",
}
