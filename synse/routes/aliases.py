"""

"""

from sanic import Blueprint

from synse import commands
from synse.version import __api_version__

bp = Blueprint(__name__, url_prefix='/synse/' + __api_version__)


# TODO - these routes still need to be implemented.


@bp.route('/led/<rack>/<board>/<device>')
async def led_route(request, rack, board, device):
    """ Endpoint to read/write LED device data.

    Args:
        request:
        rack (str):
        board (str):
        device (str):
    """
    pass


@bp.route('/fan/<rack>/<board>/<device>')
async def fan_route(request, rack, board, device):
    """ Endpoint to read/write fan device data.

    Args:
        request:
        rack (str):
        board (str):
        device (str):
    """
    pass


@bp.route('/power/<rack>/<board>/<device>')
async def power_route(request, rack, board, device):
    """ Endpoint to read/write power device data.

    Args:
        request:
        rack (str):
        board (str):
        device (str):
    """
    pass


@bp.route('/boot_target/<rack>/<board>/<device>')
async def boot_target_route(request, rack, board, device):
    """ Endpoint to read/write boot target device data.

    Args:
        request:
        rack (str):
        board (str):
        device (str):
    """
    pass
