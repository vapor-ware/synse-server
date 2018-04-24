"""Synse Server utility and convenience methods."""

import datetime

from synse.i18n import _


def rfc3339now():
    """Create an RFC3339 formatted timestamp for the current UTC time.

    See Also:
        https://stackoverflow.com/a/8556555

    Returns:
        str: The RFC3339 formatted timestamp.
    """
    now = datetime.datetime.utcnow()
    return now.isoformat('T') + 'Z'


def composite(rack, board, device):
    """Create a composite string out of a rack, board, and device.

    This can be used to uniquely identify a device across all racks.

    Args:
        rack (str): The rack associated with the device.
        board (str): The board associated with the device.
        device (str): The ID of the device.

    Returns:
        str: A composite of the input strings.
    """
    return '-'.join([rack, board, device])


def s_to_bool(val):
    """Take a string value and convert it to a boolean value.

    In Python it is not as simple as casting to a bool type since something
    like bool("false") would result in True, as a non-zero length string is
    "truthy".

    Args:
        val (str): The string value to convert to boolean.

    Returns:
        bool: True, if the string represents "true"; False otherwise.

    Raises:
        ValueError: The input parameter is not a true/false string.
    """
    if val.lower() not in ('true', 'false'):
        raise ValueError(_('"{}" is not a valid boolean string').format(val))
    return val.lower() == 'true'


def s_to_int(val):
    """Take a string value and convert it to an int.

    Converting to an integer needs to be more complex than just `int("1")`
    since we can have values like `int("1.1")` which would not get converted
    to an integer via a straight cast to `int`.

    Args:
        val (str): The string value to convert to int.

    Returns:
        int: The integer representation of the given string.

    Raises:
        ValueError: Unable to cast to int.
    """
    try:
        return int(float(val))
    except Exception as e:
        raise ValueError from e
