"""Version information and formatting.
"""

import sys

from synse import __version__

_version = __version__.split('.')

if len(_version) != 3:
    raise ValueError(
        'The version specified in the synse __init__ file must have '
        'the format: major.minor.micro.'
    )


major, minor, _ = _version

__api_version__ = major + '.' + minor

if __name__ == '__main__':
    args = sys.argv[1:]

    if args:
        if 'api' in args:
            print(__api_version__)
            exit()

    print(__version__)
