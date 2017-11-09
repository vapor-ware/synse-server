"""

"""

from sanic import Blueprint

from synse import commands
from synse.version import __api_version__

bp = Blueprint(__name__, url_prefix='/synse/' + __api_version__)


@bp.route('/info/<rack>')
@bp.route('/info/<rack>/<board>')
@bp.route('/info/<rack>/<board>/<device>')
async def info_route(request, rack, board=None, device=None):
    """

    Args:
        request:
        rack (str):
        board (str):
        device (str):
    """
    response = await commands.info(rack, board, device)
    return response.to_json()


@bp.route('/read/<rack>/<board>/<device>')
async def read_route(request, rack, board, device):
    """ Endpoint to read sensor/device data.

    Args:
        request:
        rack (str):
        board (str):
        device (str):
    """
    response = await commands.read(rack, board, device)
    return response.to_json()


@bp.route('/scan')
@bp.route('/scan/<rack>')
@bp.route('/scan/<rack>/<board>')
async def scan_route(request, rack=None, board=None):
    """

    Args:
        request:
        rack (str):
        board (str):
    """
    response = await commands.scan(rack=rack, board=board)
    return response.to_json()


@bp.route('/transaction/<transaction_id>')
async def transaction_route(request, transaction_id):
    """

    Args:
        request:
        transaction_id (str):
    """
    response = await commands.check_transaction(transaction_id)
    return response.to_json()


@bp.route('/write/<rack>/<board>/<device>', methods=['POST'])
async def write_route(request, rack, board, device):
    """

    Args:
        request:
        rack (str):
        board (str):
        device (str):
    """
    data = request.body

    response = await commands.write(rack, board, device, data)
    return response.to_json()


@bp.route('/config')
async def config_route(request):
    """

    Args:
        request:
    """
    response = await commands.config()
    return response.to_json()
