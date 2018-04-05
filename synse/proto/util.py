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


def metainfo_to_dict(meta):
    """Convert a MetainfoResponse to a dictionary that can be
    serialized out to JSON.

    Args:
        meta (MetainfoResponse): The MetainfoResponse object to
            convert to a dictionary.

    Returns:
        dict: A dictionary representation of the MetainfoResponse.
    """
    return {
        'timestamp': meta.timestamp,
        'uid': meta.uid,
        'type': meta.type,
        'model': meta.model,
        'manufacturer': meta.manufacturer,
        'protocol': meta.protocol,
        'info': meta.info,
        'comment': meta.comment,
        'location': {
            'rack': meta.location.rack,
            'board': meta.location.board
        },
        'output': [metaoutput_to_dict(o) for o in meta.output]
    }


def metaoutput_to_dict(meta):
    """Convert a MetaOutput to a dictionary that can be
    serialized out to JSON.

    Args:
        meta (MetaOutput): The MetaOutput object to
            convert to a dictionary.

    Returns:
        dict: A dictionary representation of the MetaOutput.
    """
    return {
        'type': meta.type,
        'data_type': meta.data_type,
        'precision': meta.precision,
        'unit': {
            'name': meta.unit.name,
            'symbol': meta.unit.symbol,
        },
        'range': {
            'min': meta.range.min,
            'max': meta.range.max
        }
    }
