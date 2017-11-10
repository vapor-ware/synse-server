"""Utilities around the Synse Server gRPC API.
"""

from synse_plugin import api


def write_status_name(value):
    """Get the name for a given write status value.

    Args:
        value (int): The value representing the write status.

    Returns:
        str: The string representation of the write status.
    """
    return api.WriteResponse.WriteStatus.Name(value).lower()


def write_state_name(value):
    """Get the name for a given write state value.

    Args:
        value (int): The value representing the write state.

    Returns:
        str: The string representation of the write state.
    """
    return api.WriteResponse.WriteState.Name(value).lower()
