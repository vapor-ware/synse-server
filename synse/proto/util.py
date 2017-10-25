"""

"""

from synse_plugin import api


def write_status_name(value):
    """

    Args:
        value (int):
    """
    return api.WriteResponse.WriteStatus.Name(value).lower()


def write_state_name(value):
    """

    Args:
        value (int):
    """
    return api.WriteResponse.WriteState.Name(value).lower()
