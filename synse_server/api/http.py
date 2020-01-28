"""Synse Server HTTP API."""

import ujson
from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse, StreamingHTTPResponse, stream

from synse_server import cmd, errors, utils
from synse_server.i18n import _
from synse_server.log import logger

# Blueprint for the Synse core (version-less) routes.
core = Blueprint('core-http')

# Blueprint for the Synse v3 HTTP API.
v3 = Blueprint('v3-http', version='v3')


def log_request(request, **kwargs):
    """Log information about the incoming request.

    Args:
        request: The incoming request.
        kwargs: Any additional fields to add to the structured logs.
    """
    logger.debug(
        _('processing request'),
        method=request.method,
        ip=request.ip,
        path=request.path,
        **kwargs,
    )


@core.route('/test')
async def test(request: Request) -> HTTPResponse:
    """A dependency and side-effect free check to see whether Synse Server
    is reachable and responsive.

    This endpoint does not have any internal data dependencies. A failure
    may indicate that Synse Server is not serving (e.g. still starting up
    or experiencing a failure), or that it is not reachable on the network.

    HTTP Codes:
        * 200: OK
        * 500: Catchall processing error
    """
    log_request(request)

    return utils.http_json_response(
        await cmd.test(),
    )


@core.route('/version')
async def version(request: Request) -> HTTPResponse:
    """Get the version information for the Synse Server instance.

    The API version provided by this endpoint should be used in subsequent
    versioned requests to the instance.

    HTTP Codes:
        * 200: OK
        * 500: Catchall processing error
    """
    log_request(request)

    return utils.http_json_response(
        await cmd.version(),
    )


@v3.route('/config')
async def config(request: Request) -> HTTPResponse:
    """Get the unified configuration for the Synse Server instance.

    This endpoint is provided as a convenient way to determine the settings
    that the Synse Server instance is running with. Synse Server can be configured
    with default values, values from file, and values from the environment. This
    endpoint provides the final joined configuration of all config sources.

    HTTP Codes:
        * 200: OK
        * 500: Catchall processing error
    """
    log_request(request)

    return utils.http_json_response(
        await cmd.config(),
    )


@v3.route('/plugin')
async def plugins(request: Request) -> HTTPResponse:
    """Get a summary of all the plugins currently registered with Synse Server.

    HTTP Codes:
        * 200: OK
        * 500: Catchall processing error
    """
    log_request(request)

    refresh = request.args.get('refresh', 'false').lower() == 'true'

    return utils.http_json_response(
        await cmd.plugins(
            refresh=refresh,
        ),
    )


@v3.route('/plugin/<plugin_id>')
async def plugin(request: Request, plugin_id: str) -> HTTPResponse:
    """Get detailed information on the specified plugin.

    URI Parameters:
        plugin_id: The ID of the plugin to get information for.

    HTTP Codes:
        * 200: OK
        * 404: Plugin not found
        * 500: Catchall processing error
    """
    log_request(request, id=plugin_id)

    return utils.http_json_response(
        await cmd.plugin(plugin_id),
    )


@v3.route('/plugin/health')
async def plugin_health(request: Request) -> HTTPResponse:
    """Get a summary of the health of registered plugins.

    HTTP Codes:
        * 200: OK
        * 500: Catchall processing error
    """
    log_request(request)

    return utils.http_json_response(
        await cmd.plugin_health(),
    )


@v3.route('/scan')
@v3.route('/device')
async def scan(request: Request) -> HTTPResponse:
    """List the devices that Synse knows about.

    This endpoint provides an aggregated view of all devices exposed to
    Synse Server by each of the registered plugins. By default, the scan
    results are sorted by a combination key of 'plugin,sortIndex,id'.

    Query Parameters:
        ns: The default namespace to use for specified tags without explicit namespaces.
            Only one default namespace may be specified. (default: ``default``)
        tags: The tags to filter devices by. Multiple tag groups may be specified by
            providing multiple ``tags`` query parameters, e.g. ``?tags=foo&tags=bar``.
            Each tag group may consist of one or more comma-separated tags. Each tag
            group only selects devices which match all of the tags in the group. If
            multiple tag groups are specified, the result is the union of the matches
            from each individual tag group.
        force: Force a re-scan (rebuild the internal cache). This will take longer than
            a scan which uses the cache. (default: false)
        sort: Specify the fields to sort by. Multiple fields may be specified as a
            comma-separated string, e.g. "plugin,id". The "tags" field can not be used
            for sorting. (default: "plugin,sortIndex,id", where ``sortIndex`` is an
            internal sort preference which a plugin can optionally specify.)

    HTTP Codes:
        * 200: OK
        * 400: Invalid parameter(s)
        * 500: Catchall processing error
    """
    log_request(request, params=request.args)

    namespace = 'default'
    param_ns = request.args.getlist('ns')
    if param_ns:
        if len(param_ns) > 1:
            raise errors.InvalidUsage(
                'invalid parameter: only one namespace may be specified',
            )
        namespace = param_ns[0]

    tag_groups = []
    param_tags = request.args.getlist('tags')
    if param_tags:
        for group in param_tags:
            tag_groups.append(group.split(','))

    force = request.args.get('force', 'false').lower() == 'true'

    sort_keys = 'plugin,sortIndex,id'
    param_sort = request.args.getlist('sort')
    if param_sort:
        if len(param_sort) > 1:
            raise errors.InvalidUsage(
                'invalid parameter: only one sort key may be specified',
            )
        sort_keys = param_sort[0]

    return utils.http_json_response(
        await cmd.scan(
            ns=namespace,
            tag_groups=tag_groups,
            force=force,
            sort=sort_keys,
        ),
    )


@v3.route('/tags')
async def tags(request: Request) -> HTTPResponse:
    """List all of the tags which are currently associated with devices
    in the system.

    By default, all non-ID tags are listed.

    Query Parameters:
        ns: The tag namespace(s) to use when searching for tags. If specifying multiple
            namespaces, they can be passed in as a comma-separated list, e.g.
            ``?ns=ns1,ns2,ns3``, or via multiple ``ns`` parameters, e.g.
            ``?ns=ns1&ns=ns2&ns=ns3``. (default: ``default``)
        ids: A flag which determines whether ``id`` tags are included in the
            response. (default: ``false``)

    HTTP Codes:
        * 200: OK
        * 500: Catchall processing error
    """
    log_request(request, params=request.args)

    namespaces = []
    param_ns = request.args.getlist('ns')
    if param_ns:
        for namespace in param_ns:
            namespaces.extend(namespace.split(','))

    include_ids = request.args.get('ids', 'false').lower() == 'true'

    return utils.http_json_response(
        await cmd.tags(
            namespaces,
            with_id_tags=include_ids,
        ),
    )


@v3.route('/info/<device_id>')
async def info(request: Request, device_id: str) -> HTTPResponse:
    """Get detailed information about the specified device.

    URI Parameters:
        device_id: The ID of the device to get information for.

    HTTP Codes:
        * 200: OK
        * 404: Device not found
        * 500: Catchall processing error
    """
    log_request(request, id=device_id)

    return utils.http_json_response(
        await cmd.info(device_id),
    )


@v3.route('/read')
async def read(request: Request) -> HTTPResponse:
    """Read data from devices which match the set of provided tags.

    Reading data is returned for only those devices which match all of the
    specified tags.

    Query Parameters:
        ns: The default namespace to use for specified tags without explicit namespaces.
            Only one default namespace may be specified. (default: ``default``)
        tags: The tags to filter devices by. Multiple tag groups may be specified by
            providing multiple ``tags`` query parameters, e.g. ``?tags=foo&tags=bar``.
            Each tag group may consist of one or more comma-separated tags. Each tag
            group only selects devices which match all of the tags in the group. If
            multiple tag groups are specified, the result is the union of the matches
            from each individual tag group.

    HTTP Codes:
        * 200: OK
        * 400: Invalid parameter(s)
        * 500: Catchall processing error
    """
    log_request(request, params=request.args)

    namespace = 'default'
    param_ns = request.args.getlist('ns')
    if param_ns:
        if len(param_ns) > 1:
            raise errors.InvalidUsage(
                'invalid parameter: only one default namespace may be specified',
            )
        namespace = param_ns[0]

    tag_groups = []
    param_tags = request.args.getlist('tags')
    if param_tags:
        for group in param_tags:
            tag_groups.append(group.split(','))

    return utils.http_json_response(
        await cmd.read(
            ns=namespace,
            tag_groups=tag_groups,
        ),
    )


@v3.route('/readcache')
async def read_cache(request: Request) -> StreamingHTTPResponse:
    """Stream cached reading data from the registered plugins.

    Plugins may optionally cache readings for a given time window. This endpoint
    exposes the data in that cache. If a readings cache is not configured for a
    plugin, a snapshot of its current reading state is streamed back in the response.

    Query Parameters:
        start: An RFC3339 formatted timestamp which specifies a starting bound on the
            cache data to return. If left unspecified, there will be no starting bound.
        end: An RFC3339 formatted timestamp which specifies an ending bound on the
            cache data to return. If left unspecified, there will be no ending bound.

    HTTP Codes:
        * 200: OK
        * 400: Invalid query parameter(s)
        * 500: Catchall processing error
    """
    log_request(request, params=request.args)

    start = ''
    param_start = request.args.getlist('start')
    if param_start:
        if len(param_start) > 1:
            raise errors.InvalidUsage(
                'invalid parameter: only one cache start may be specified',
            )
        start = param_start[0]

    end = ''
    param_end = request.args.getlist('end')
    if param_end:
        if len(param_end) > 1:
            raise errors.InvalidUsage(
                'invalid parameter: only one cache end may be specified',
            )
        end = param_end[0]

    # Define the function that will be used to stream the responses back.
    async def response_streamer(response):
        # Due to how streamed responses are handled, an exception here won't
        # end up surfacing to the user through Synse's custom error handler
        # and instead appear to create an opaque error relating to an invalid
        # character in the chunk header. Instead of surfacing that error, we
        # just log it and move on.
        try:
            async for reading in cmd.read_cache(start, end):
                await response.write(ujson.dumps(reading) + '\n')
        except Exception as e:
            logger.error('failure when streaming cached readings')
            logger.exception(e)

    return stream(response_streamer, content_type='application/json; charset=utf-8')


@v3.route('/read/<device_id>')
async def read_device(request: Request, device_id: str) -> HTTPResponse:
    """Read from the specified device.

    This endpoint is equivalent to the ``read`` endpoint, specifying the ID tag
    for the device.

    URI Parameters:
        device_id: The ID of the device to read.

    HTTP Codes:
        * 200: OK
        * 404: Device not found
        * 405: Device does not support reading
        * 500: Catchall processing error
    """
    log_request(request, id=device_id)

    return utils.http_json_response(
        await cmd.read_device(device_id),
    )


@v3.route('/write/<device_id>', methods=['POST'])
async def async_write(request: Request, device_id: str) -> HTTPResponse:
    """Write data to a device in an asynchronous manner.

    The write will generate a transaction ID for each write payload to the
    specified device. The transaction can be checked later via the ``transaction``
    endpoint.

    URI Parameters:
        device_id: The ID of the device that is being written to.

    HTTP Codes:
        * 200: OK
        * 400: Invalid JSON provided
        * 404: Device not found
        * 405: Device does not support writing
        * 500: Catchall processing error
    """
    log_request(request, id=device_id, payload=request.body)

    try:
        data = request.json
    except Exception as e:
        raise errors.InvalidUsage(
            'invalid json: unable to parse POSTed body as JSON'
        ) from e

    # Validate that the incoming payload has an 'action' field defined. This
    # field is required. All other fields are optional.
    if isinstance(data, dict):
        data = [data]
    for item in data:
        if 'action' not in item:
            raise errors.InvalidUsage(
                'invalid json: key "action" is required in payload, but not found'
            )

    return utils.http_json_response(
        await cmd.write_async(
            device_id=device_id,
            payload=data,
        ),
    )


@v3.route('/write/wait/<device_id>', methods=['POST'])
async def sync_write(request: Request, device_id: str) -> HTTPResponse:
    """Write data to a device synchronously, waiting for the write to complete.

    The length of time it takes for a write to complete depends on both the device
    and its plugin. It is up to the caller to define a sane request timeout so the
    request does not prematurely terminate.

    URI Parameters:
        device_id: The ID of the device that is being written to.

    HTTP Codes:
        * 200: OK
        * 400: Invalid JSON provided
        * 404: Device not found
        * 405: Device does not support writing
        * 500: Catchall processing error
    """
    log_request(request, id=device_id, payload=request.body)

    try:
        data = request.json
    except Exception as e:
        raise errors.InvalidUsage(
            'invalid json: unable to parse POSTed body as JSON'
        ) from e

    # Validate that the incoming payload has an 'action' field defined. This
    # field is required. All other fields are optional.
    if isinstance(data, dict):
        data = [data]
    for item in data:
        if 'action' not in item:
            raise errors.InvalidUsage(
                'invalid json: key "action" is required in payload, but not found'
            )

    return utils.http_json_response(
        await cmd.write_sync(
            device_id=device_id,
            payload=data,
        ),
    )


@v3.route('/transaction')
async def transactions(request: Request) -> HTTPResponse:
    """Get a list of all transactions currently being tracked by Synse Server.

    HTTP Codes:
        * 200: OK
        * 500: Catchall processing error
    """
    log_request(request)

    return utils.http_json_response(
        await cmd.transactions(),
    )


@v3.route('/transaction/<transaction_id>')
async def transaction(request: Request, transaction_id: str) -> HTTPResponse:
    """Get the status of a write transaction.

    URI Parameters:
        transaction_id: The ID of the write transaction to get the status of.

    HTTP Codes:
        * 200: OK
        * 404: Transaction not found
        * 500: Catchall processing error
    """
    log_request(request, id=transaction_id)

    return utils.http_json_response(
        await cmd.transaction(transaction_id),
    )


@v3.route('/device/<device_id>', methods=['GET', 'POST'])
async def device(request: Request, device_id: str) -> HTTPResponse:
    """Read or write to the specified device.

    This endpoint provides read/write access to all devices via their deterministic
    GUID. The underlying implementations for read and write are the same as the
    ``/read/{device}`` and ``/write/wait/{device}`` endpoints, respectively.

    URI Parameters:
        device_id: The ID of the device that is being read from/written to.

    HTTP Codes:
        * 200: OK
        * 400: Invalid JSON provided / Invalid parameter(s)
        * 404: Device not found
        * 405: Device does not support reading/writing
        * 500: Catchall processing error
    """
    log_request(request, id=device_id)

    if request.method == 'GET':
        return await read_device(request, device_id)

    else:
        return await sync_write(request, device_id)
