"""Utilities around the Synse Server gRPC API."""

from synse_grpc import api


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


def plugin_health_status_name(value):
    """Get the name for the given health state value.

    Args:
        value (int): The value representing the health state.

    Returns:
        str: The string representation of the health state.
    """
    return api.PluginHealth.Status.Name(value).lower()


def device_info_to_dict(device):
    """Convert a grpc Device to a dictionary that can be serialized out
    to JSON.

    Args:
        device (Device): The Device object to convert to a dictionary.

    Returns:
        dict: A dictionary representation of the Device.
    """
    return {
        'timestamp': device.timestamp,
        'uid': device.uid,
        'kind': device.kind,
        'metadata': device.metadata,
        'plugin': device.plugin,
        'info': device.info,
        'location': {
            'rack': device.location.rack,
            'board': device.location.board
        },
        'output': [output_to_dict(o) for o in device.output]
    }


def output_to_dict(output):
    """Convert an Output to a dictionary that can be serialized out to JSON.

    Args:
        output (Output): The Output object to convert to a dictionary.

    Returns:
        dict: A dictionary representation of the Output.
    """
    return {
        'name': output.name,
        'type': output.type,
        'precision': output.precision,
        'scaling_factor': output.scalingFactor,
        'unit': {
            'name': output.unit.name,
            'symbol': output.unit.symbol,
        },
    }
