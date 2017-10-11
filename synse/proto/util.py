"""

"""

from synse.proto import api_pb2


def reading_type_name(value):
    """ Get the string name for the given ReadingType enum value.

    The name will be returned as a lower cased string.

    Args:
        value (int): the protobuf-assigned int for the ReadingType enum
            value for which we want to get the string name for.
    """
    return api_pb2.ReadingType.Name(value).lower()


def write_status_name(value):
    """

    Args:
        value (int):
    """
    return api_pb2.WriteResponse.WriteStatus.Name(value).lower()


def write_state_name(value):
    """

    Args:
        value (int):
    """
    return api_pb2.WriteResponse.WriteState.Name(value).lower()
