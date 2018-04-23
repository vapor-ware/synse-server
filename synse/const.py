"""Synse Server application-wide constants."""

# QUESTION (etd) - should this be 'procs', or something else? perhaps 'run' or 'sock'
SOCKET_DIR = '/tmp/synse/procs'

# Device Types
TYPE_LED = 'led'
TYPE_FAN = 'fan'
TYPE_SYSTEM = 'system'
TYPE_POWER = 'power'
TYPE_LOCK = 'lock'


# LED state definitions
LED_ON = 'on'
LED_OFF = 'off'
LED_BLINK = 'blink'

# all LED states
led_states = (
    LED_ON,
    LED_OFF,
    LED_BLINK
)


# Power action definitions
PWR_ON = 'on'
PWR_OFF = 'off'
PWR_CYCLE = 'cycle'

# all power actions
power_actions = (
    PWR_ON,
    PWR_OFF,
    PWR_CYCLE
)


# Supported boot target definitions
BT_HDD = 'hdd'
BT_PXE = 'pxe'

# all boot targets
boot_targets = (
    BT_HDD,
    BT_PXE
)


# Lock action definitions
LOCK_LOCK = 'lock'
LOCK_UNLOCK = 'unlock'
LOCK_MUNLOCK = 'munlock'  # momentary unlock

# all lock actions
lock_actions = (
    LOCK_LOCK,
    LOCK_UNLOCK,
    LOCK_MUNLOCK
)
