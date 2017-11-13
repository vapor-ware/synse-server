"""The core routes that make up the Synse Server JSON API.
"""

from sanic import Blueprint

from synse import commands
from synse import errors
from synse.log import logger
from synse.version import __api_version__

bp = Blueprint(__name__, url_prefix='/synse/' + __api_version__)


@bp.route('/scan')
@bp.route('/scan/<rack>')
@bp.route('/scan/<rack>/<board>')
async def scan_route(request, rack=None, board=None):
    """Get meta-information about all racks, boards, and devices from all
    configured plugins.

    This aggregates the known configured racks, boards, and devices for
    each of the running plugins providing information to Synse Server. The
    scan response provides a high-level view of which devices exist in the
    system and where they exist (e.g. how they are addressable). With a scan
    response, a user should have enough information to perform any subsequent
    command (e.g. read, write) for a given device.

    Args:
        request:
        rack (str): The identifier of the rack to scan. If specified, this
            filters the complete scan result to only return the subset of
            scan information pertinent to the specific rack.
        board (str): The identifier of the board to scan. If specified, in
            conjunction with a rack identifier, this filters the complete
            scan result to only return the scan information for the specified
            board on the specified rack.
    """
    param_force = request.raw_args.get('force')
    if param_force is not None:
        force = param_force.lower() == 'true'
        logger.debug('forcing re-scan? {}'.format(force))
    else:
        force = False

    response = await commands.scan(rack=rack, board=board, force=force)
    return response.to_json()


@bp.route('/read/<rack>/<board>/<device>')
async def read_route(request, rack, board, device):
    """Read data from a known device.

    Args:
        request:
        rack (str): The identifier of the rack which the device resides on.
        board (str): The identifier of the board which the device resides on.
        device (str): The identifier of the device to read.
    """
    response = await commands.read(rack, board, device)
    return response.to_json()


@bp.route('/write/<rack>/<board>/<device>', methods=['POST'])
async def write_route(request, rack, board, device):
    """Write data to a known device.

    The data POSTed here should be JSON with an 'action' field  and 'raw'
    field, if applicable. If no data is posted, the write will fail.

    Args:
        request:
        rack (str): The identifier of the rack which the device resides on.
        board (str): The identifier of the board which the device resides on.
        device (str): The identifier of the device to write to.
    """
    # FIXME - probably want a try/except?
    data = request.json
    logger.debug('WRITE -> json: {}'.format(data))

    if not any([x in data for x in ['action', 'raw']]):
        raise errors.SynseError('Invalid data POSTed for write. Must contain "action" and/or "raw".')

    response = await commands.write(rack, board, device, data)
    return response.to_json()


@bp.route('/transaction/<transaction_id>')
async def transaction_route(request, transaction_id):
    """Check the status of a write transaction.

    Args:
        request:
        transaction_id (str): The ID of the transaction to check.
    """
    response = await commands.check_transaction(transaction_id)
    return response.to_json()


@bp.route('/info/<rack>')
@bp.route('/info/<rack>/<board>')
@bp.route('/info/<rack>/<board>/<device>')
async def info_route(request, rack, board=None, device=None):
    """Get any known information on the specified resource.

    Args:
        request:
        rack (str): The identifier for the rack to find info for.
        board (str): The identifier for the board to find info for.
        device (str): The identifier for the device to find info for.
    """
    response = await commands.info(rack, board, device)
    return response.to_json()


@bp.route('/config')
async def config_route(request):
    """Get the current Synse Server configuration.

    Args:
        request:
    """
    response = await commands.config()
    return response.to_json()
