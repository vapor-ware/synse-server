"""Synse Server commands package.

This package contains the command definitions for all Synse Server
endpoints.

Command functions are imported here for easier importing elsewhere,
e.g. instead of having to do 'from synse.commands.scan import scan'
you can simply 'from synse.commands import scan'.
"""

from .capabilities import capabilities
from .config import config
# FIXME (etd) - temporary for autofan support
from .fan_sensors import fan_sensors
from .info import info
from .plugins import get_plugins
from .read import read
from .read_cached import read_cached
from .scan import scan
from .test import test
from .transaction import check_transaction
from .version import version
from .write import write
