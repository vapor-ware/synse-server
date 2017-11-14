"""The aliased routes that make up the Synse Server JSON API.
"""
# pylint: disable=unused-argument

from sanic import Blueprint

from synse.version import __api_version__

bp = Blueprint(__name__, url_prefix='/synse/' + __api_version__)


# TODO - these routes still need to be implemented.


@bp.route('/led/<rack>/<board>/<device>')
async def led_route(request, rack, board, device):
    """ Endpoint to read/write LED device data.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the led device resides on.
        board (str): The board which the led device resides on.
        device (str): The LED device.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    pass


@bp.route('/fan/<rack>/<board>/<device>')
async def fan_route(request, rack, board, device):
    """ Endpoint to read/write fan device data.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the fan device resides on.
        board (str): The board which the fan device resides on.
        device (str): The fan device.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    pass


@bp.route('/power/<rack>/<board>/<device>')
async def power_route(request, rack, board, device):
    """ Endpoint to read/write power device data.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the power device resides on.
        board (str): The board which the power device resides on.
        device (str): The power device.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    pass


@bp.route('/boot_target/<rack>/<board>/<device>')
async def boot_target_route(request, rack, board, device):
    """ Endpoint to read/write boot target device data.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the system resides on.
        board (str): The board which the system resides on.
        device (str): The system device.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    pass
