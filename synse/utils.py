"""Synse Server utility and convenience methods."""

import datetime


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
