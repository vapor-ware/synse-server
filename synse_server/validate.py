"""Synse Server utility and convenience methods."""

from functools import wraps

from synse_server import cache, errors
from synse_server.i18n import _


async def validate_device_type(device_type, rack, board, device):
    """Validate that the device associated with the given routing info
    (rack, board device) matches the given device type.

    This checks that the lower-cased device type matches the lower-cased
    expected type, so casing on device type(s) should not matter.

    Args:
        device_type (list[str]): The device types that are permissible,
            e.g. "led", "fan", etc.
        rack (str): The rack which the device belongs to.
        board (str): The board which the device belongs to.
        device (str): The ID of the device.

    Raises:
        errors.InvalidDeviceType: The device does not match the given type.
        errors.DeviceNotFoundError: The specified device is not found.
    """
    __, device = await cache.get_device_info(rack, board, device)  # pylint: disable=unused-variable

    # The type of a device should be the last element in it's kind namespace.
    _type = device.kind.split('.')[-1].lower()
    if _type not in [t.lower() for t in device_type]:
        raise errors.ServerError(
            _('Device ({}) is not a supported type {}').format(_type, device_type)
        )


def validate_query_params(raw_args, *valid_params):
    """Validate that the incoming request's query parameters are valid.

    Any unsupported query parameter will cause an error to be raised.
    Absence of a supported query parameter will not cause an error. If
    a supported query parameter is found, it is added to the response
    dictionary.

    Args:
        raw_args: An incoming Sanic request's `raw_args`, which contains the
            query params that came in as part of the request.
        *valid_params: The query parameter keys that are valid for the request.

    Returns:
        dict: A dictionary that maps the supported query parameters found in
            the request with their values.

    Raises:
        errors.InvalidArgumentsError: An invalid query parameter was detected.
    """
    params = {}
    for k, v in raw_args.items():
        if k not in valid_params:
            raise errors.InvalidUsage(
                _('Invalid query param: {} (valid params: {})').format(k, valid_params)
            )
        params[k] = v
    return params


def no_query_params():
    """Decorator to validate that the incoming request has no query parameters.

    This check is largely to ensure that the API is being used correctly
    and params aren't accidentally being passed where they don't belong.

    Raises:
        errors.InvalidArgumentsError: Query parameters were found with
            the request.
    """
    def decorator(f):  # pylint: disable=missing-docstring
        @wraps(f)
        async def inner(request, *args, **kwargs):  # pylint: disable=missing-docstring
            if len(request.raw_args) != 0:
                raise errors.InvalidUsage(
                    _('Endpoint does not support query parameters but got: {}').format(
                        request.raw_args)
                )
            return await f(request, *args, **kwargs)
        return inner
    return decorator
