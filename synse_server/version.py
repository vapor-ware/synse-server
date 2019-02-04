"""Version information and formatting."""

from synse_server import __version__

_version = __version__.split('.')

if len(_version) != 3:
    raise ValueError(
        'The version specified in the synse __init__ file must have '
        'the format: major.minor.micro.'
    )


major, minor, __ = _version

__api_version__ = 'v' + major
