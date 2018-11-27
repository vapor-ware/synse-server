"""Synse Server application-wide constants."""

# QUESTION (etd) - should this be 'procs', or something else? perhaps 'run' or 'sock'
SOCKET_DIR = '/tmp/synse/procs'

# Device type definitions
TYPE_LED = 'led'
TYPE_FAN = 'fan'
TYPE_SYSTEM = 'system'
TYPE_POWER = 'power'
TYPE_LOCK = 'lock'
TYPE_BOOT_TARGET = 'boot_target'

# Type groupings (these correspond to API actions)
LED_TYPES = [TYPE_LED]
FAN_TYPES = [TYPE_FAN]
POWER_TYPES = [TYPE_POWER]
LOCK_TYPES = [TYPE_LOCK]
BOOT_TARGET_TYPES = [TYPE_SYSTEM, TYPE_BOOT_TARGET]


# LED state definitions
LED_ON = 'on'
LED_OFF = 'off'
LED_BLINK = 'blink'

# All LED states
led_states = (
    LED_ON,
    LED_OFF,
    LED_BLINK
)


# Power action definitions
PWR_ON = 'on'
PWR_OFF = 'off'
PWR_CYCLE = 'cycle'

# All power actions
power_actions = (
    PWR_ON,
    PWR_OFF,
    PWR_CYCLE
)


# Supported boot target definitions
BT_HDD = 'hdd'
BT_PXE = 'pxe'

# All boot targets
boot_targets = (
    BT_HDD,
    BT_PXE
)


# Lock action definitions
LOCK_LOCK = 'lock'
LOCK_UNLOCK = 'unlock'
LOCK_PULSEUNLOCK = 'pulseUnlock'

# All lock actions
lock_actions = (
    LOCK_LOCK,
    LOCK_UNLOCK,
    LOCK_PULSEUNLOCK,
)
