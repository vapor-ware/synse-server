"""The core routes that make up the Synse Server HTTP API."""
# pylint: disable=unused-argument

from sanic import Blueprint
from sanic.response import stream

from synse import commands, errors, validate
from synse.i18n import _
from synse.log import logger
from synse.response import json
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

    Supported Query Parameters:
        force: Forces a re-scan if 'true', otherwise does nothing.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The identifier of the rack to scan. If specified, this
            filters the complete scan result to only return the subset of
            scan information pertinent to the specific rack.
        board (str): The identifier of the board to scan. If specified, in
            conjunction with a rack identifier, this filters the complete
            scan result to only return the scan information for the specified
            board on the specified rack.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    qparams = validate.validate_query_params(request.raw_args, 'force')

    param_force = qparams.get('force')

    force = False
    if param_force is not None:
        force = param_force.lower() == 'true'
    logger.debug(_('Forcing re-scan? {}').format(force))

    response = await commands.scan(rack=rack, board=board, force=force)
    return response.to_json()


@bp.route('/read/<rack>/<board>/<device>')
@validate.no_query_params()
async def read_route(request, rack, board, device):
    """Read data from a known device.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The identifier of the rack which the device resides on.
        board (str): The identifier of the board which the device resides on.
        device (str): The identifier of the device to read.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    response = await commands.read(rack, board, device)
    return response.to_json()


@bp.route('/readcached')
async def read_cached_route(request):
    """Get cached readings from the configured plugins.

    Query Parameters:
        start: An RFC3339 or RFC3339Nano formatted timestamp which specifies a
            starting bound on the cache data to return. If no timestamp is
            specified, there will not be a starting bound.
        end: An RFC3339 or RFC3339Nano formatted timestamp which specifies an
            ending bound on the cache data to return. If no timestamp is
            specified, there will not be an ending bound.
    """
    qparams = validate.validate_query_params(request.raw_args, 'start', 'end')
    start, end = qparams.get('start'), qparams.get('end')

    # define the streaming function
    async def response_streamer(response):
        async for reading in commands.read_cached(start, end):  # pylint: disable=not-an-iterable
            await response.write(reading.dump())

    return stream(response_streamer, content_type='application/json')


@bp.route('/write/<rack>/<board>/<device>', methods=['POST'])
@validate.no_query_params()
async def write_route(request, rack, board, device):
    """Write data to a known device.

    The data POSTed here should be JSON with an 'action' field  and 'raw'
    field, if applicable. If no data is posted, the write will fail.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The identifier of the rack which the device resides on.
        board (str): The identifier of the board which the device resides on.
        device (str): The identifier of the device to write to.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    try:
        data = request.json
    except Exception as e:
        raise errors.InvalidJsonError(
            _('Invalid JSON specified: {}').format(request.body)
        ) from e

    logger.debug(_('Write route: POSTed JSON: {}').format(data))

    # For backwards compatibility, keeping 'raw' in. Here, 'data' and 'raw' are
    # the same thing.
    if not any([x in data for x in ['action', 'raw', 'data']]):
        raise errors.InvalidArgumentsError(
            _('Invalid data POSTed for write. Must contain "action" and/or "raw"')
        )

    response = await commands.write(rack, board, device, data)
    return response.to_json()


@bp.route('/transaction')
@bp.route('/transaction/<transaction_id>')
@validate.no_query_params()
async def transaction_route(request, transaction_id=None):
    """Check the status of a write transaction.

    Args:
        request (sanic.request.Request): The incoming request.
        transaction_id (str): The ID of the transaction to check.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    response = await commands.check_transaction(transaction_id)
    return response.to_json()


@bp.route('/info/<rack>')
@bp.route('/info/<rack>/<board>')
@bp.route('/info/<rack>/<board>/<device>')
@validate.no_query_params()
async def info_route(request, rack, board=None, device=None):
    """Get any known information on the specified resource.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The identifier for the rack to find info for.
        board (str): The identifier for the board to find info for.
        device (str): The identifier for the device to find info for.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    response = await commands.info(rack, board, device)
    return response.to_json()


@bp.route('/config')
@validate.no_query_params()
async def config_route(request):
    """Get the current Synse Server configuration.

    Args:
        request (sanic.request.Request): The incoming request.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    response = await commands.config()
    return response.to_json()


@bp.route('/plugins')
@validate.no_query_params()
async def plugins_route(request):
    """Get the plugins that are currently configured with Synse Server.

    Args:
        request (sanic.request.Request): The incoming request.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    response = await commands.get_plugins()
    return response.to_json()


@bp.route('/capabilities')
@validate.no_query_params()
async def capabilities_route(request):
    """Enumerate the device capabilities provided by all of the registered plugins.

    Args:
        request (sanic.request.Request): The incoming request.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    response = await commands.capabilities()
    return response.to_json()


# FIXME (etd) -- this is a temporary route that is being used for auto-fan for demo/
# development. this functionality should be generalized and this specific endpoint
# should be removed. this will only stay in for a short period of time, so use at
# your own risk!
@bp.route('/fan_sensors')
@validate.no_query_params()
async def fan_sensors(request):
    """Get fan sensor data for autofan.

    FIXME: this is a temporary route for autofan -- this should be generalized
    and we can add it back into mainline synse server.
    """
    result = await commands.fan_sensors()
    return json(result)
