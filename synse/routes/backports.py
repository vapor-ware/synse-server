"""The backports routes that make up the Synse Server JSON API.

These routes provide support for older style (e.g. v1.4) routes. This
primarily adds in routes that allow the user to set values for well
known devices (e.g. LED, fan) via GET requests, which were removed
from version 2.0 in favor of a more REST-like API.
"""
# pylint: disable=no-else-return

from sanic import Blueprint
from sanic.request import RequestParameters

from synse.routes import aliases
from synse.version import __api_version__

bp = Blueprint(__name__, url_prefix='/synse/' + __api_version__)


@bp.route('/led/<rack>/<board>/<device>/<state>')
@bp.route('/led/<rack>/<board>/<device>/<state>/<color>/<blink>')
async def backport_led_route(request, rack, board, device, state, color=None, blink=None):
    """Endpoint to read/write LED device data.

    These routes are ported from Synse v1.4.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the led device resides on.
        board (str): The board which the led device resides on.
        device (str): The LED device.
        state (str): The state to set the LED to (on|off).
        color (str): The hex RGB color to set the LED to.
        blink (str): The blink state to set the LED to
            (blink|steady|no_override).

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    request.parsed_args = RequestParameters(dict(
        state=[state],
        blink=[blink],
        color=[color]
    ))

    resp = await aliases.led_route(request, rack, board, device)
    return resp


@bp.route('/fan/<rack>/<board>/<device>/<speed>')
async def backport_fan_route(request, rack, board, device, speed):
    """Endpoint to read/write fan device data.

    This route is ported from Synse v1.4

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the fan device resides on.
        board (str): The board which the fan device resides on.
        device (str): The fan device.
        speed (str): The speed to set the fan to.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    request.parsed_args = RequestParameters(dict(speed=[speed]))

    resp = await aliases.fan_route(request, rack, board, device)
    return resp


@bp.route('/boot_target/<rack>/<board>/<device>/<target>')
async def backport_boot_target_route(request, rack, board, device, target):
    """Endpoint to read/write boot target device data.

    This route is ported from Synse v1.4

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the system resides on.
        board (str): The board which the system resides on.
        device (str): The system device.
        target (str): The boot target to choose.
            (pxe|hdd|no_override)

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    request.parsed_args = RequestParameters(dict(target=[target]))

    resp = await aliases.boot_target_route(request, rack, board, device)
    return resp
