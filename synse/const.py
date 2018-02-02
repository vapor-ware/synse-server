"""Synse Server application-wide constants.
"""

# QUESTION (etd) - should this be 'procs', or something else? perhaps 'run' or 'sock'
SOCKET_DIR = '/tmp/synse/procs'

# Device Types
TYPE_LED = 'led'
TYPE_FAN = 'fan'
TYPE_SYSTEM = 'system'
TYPE_POWER = 'power'


# LED states
LED_ON = 'on'
LED_OFF = 'off'
LED_BLINK = 'blink'
LED_STEADY = 'steady'
LED_NO_OVERRIDE = 'no_override'


# power actions
PWR_ON = 'on'
PWR_OFF = 'off'
PWR_CYCLE = 'cycle'


# supported boot targets
BT_HDD = 'hdd'
BT_PXE = 'pxe'
