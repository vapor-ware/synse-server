"""Synse Server HTTP API."""

from sanic import Blueprint
from sanic.response import text

from synse_server.log import logger
from synse_server import cmd, utils
from synse_server.i18n import _

# Blueprint for the Synse core (version-less) routes.
core = Blueprint('core-http')

# Blueprint for the Synse v3 HTTP API.
v3 = Blueprint('v3-http', version='v3')


@core.route('/test')
async def test(request):
    """A dependency and side-effect free check to see whether Synse Server
    is reachable and responsive.

    This endpoint does not have any internal data dependencies. A failure
    may indicate that Synse Server is not serving (e.g. still starting up
    or experiencing a failure), or that it is not reachable on the network.

    HTTP Codes:
        * 200: OK
        * 500: Catchall processing error
    """
    logger.debug(_('processing request'), endpoint='/test')

    return utils.http_json_response(
        await cmd.test(),
    )


@core.route('/version')
async def version(request):
    """Get the version information for the Synse Server instance.

    The API version provided by this endpoint should be used in subsequent
    versioned requests to the instance.

    HTTP Codes:
        * 200: OK
        * 500: Catchall processing error
    """
    logger.debug(_('processing request'), endpoint='/version')

    return utils.http_json_response(
        await cmd.version(),
    )


@v3.route('/config')
async def config(request):
    """Get the unified configuration for the Synse Server instance.

    This endpoint is provided as a convenient way to determine the settings
    that the Synse Server instance is running with. Synse Server can be configured
    with default values, values from file, and values from the environment. This
    endpoint provides the final joined configuration of all config sources.

    HTTP Codes:
        * 200: OK
        * 500: Catchall processing error
    """
    logger.debug(_('processing request'), endpoint='/v3/config')

    return utils.http_json_response(
        await cmd.config(),
    )


@v3.route('/plugin')
async def plugins(request):
    """Get a summary of all the plugins currently registered with Synse Server.

    HTTP Codes:
        * 200: OK
        * 500: Catchall processing error
    """
    logger.debug(_('processing request'), endpoint='/v3/plugin')

    return utils.http_json_response(
        await cmd.plugins(),
    )


@v3.route('/plugin/<plugin_id>')
async def plugin(request, plugin_id):
    """Get detailed information on the specified plugin.

    URI Parameters:
        plugin_id: The ID of the plugin to get information for.

    HTTP Codes:
        * 200: OK
        * 404: Plugin not found
        * 500: Catchall processing error
    """
    logger.debug(_('processing request'), endpoint='/v3/plugin/<id>', id=plugin_id)

    return utils.http_json_response(
        await cmd.plugin(plugin_id),
    )


@v3.route('/plugin/health')
async def plugin_health(request):
    """Get a summary of the health of registered plugins.

    HTTP Codes:
        * 200: OK
        * 500: Catchall processing error
    """
    logger.debug(_('processing request'), endpoint='/v3/plugin/health')

    return utils.http_json_response(
        await cmd.plugin_health(),
    )


@v3.route('/scan')
async def scan(request):
    """List the devices that Synse knows about,

    This endpoint provides an aggregated view of all devices exposed to
    Synse Server by each of the registered plugins. By default, the scan
    results are sorted by a combination key of 'plugin,sort_index,id'.

    Query Parameters:
        ns: The default namespace to use for specified tags without explicit namespaces.
            Only one default namespace may be specified. (default: ``default``)
        tags: The tags to filter devices on. If specifying multiple tags, they can
            be passed in as a comma-separated list, e.g. ``?tags=tag1,tag2,tag3``,
            or via multiple ``tags`` parameters, e.g. ``?tags=tag1&tags=tag2&tags=tag3``.
        force: Force a re-scan (rebuild the internal cache). This will take longer than
            a scan which uses the cache. (default: false)
        sort: Specify the fields to sort by. Multiple fields may be specified as a
            comma-separated string, e.g. "plugin,id". The "tags" field can not be used
            for sorting. (default: "plugin,sort_index,id", where ``sort_index`` is an
            internal sort preference which a plugin can optionally specify.)

    HTTP Codes:
        * 200: OK
        * 400: Invalid parameter(s)
        * 500: Catchall processing error
    """
    logger.debug(_('processing request'), endpoint='/v3/scan', params=request.args)

    namespace = 'default'
    param_ns = request.args.get('ns')
    if param_ns:
        if len(param_ns) > 1:
            # FIXME: 400 invalid param
            raise ValueError
        namespace = param_ns[0]

    tags = []
    param_tags = request.args.get('tags')
    if param_tags:
        for tag in param_tags:
            tags.extend(tag.split(','))

    force = request.args.get('force', 'false').lower() == 'true'

    sort_keys = 'plugin,sort_index,id'
    param_sort = request.args.get('sort')
    if param_sort:
        if len(param_sort) > 1:
            # FIXME 400 invalid param
            raise ValueError
        sort_keys = param_sort[0]

    return utils.http_json_response(
        await cmd.scan(
            ns=namespace,
            tags=tags,
            force=force,
            sort=sort_keys,
        ),
    )


@v3.route('/tags')
async def tags(request):
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
        * 400: Invalid parameter(s)
        * 500: Catchall processing error
    """
    logger.debug(_('processing request'), endpoint='/v3/tags', params=request.args)

    namespaces = []
    param_ns = request.args.get('ns')
    if param_ns:
        for namespace in param_ns:
            namespaces.extend(namespace.split(','))

    include_ids = request.args.get('ids', 'false').lower() == 'true'

    return utils.http_json_response(
        await cmd.tags(
            *namespaces,
            with_id_tags=include_ids,
        ),
    )


@v3.route('/info/<device_id>')
async def info(request, device_id):
    """Get detailed information about the specified device.

    URI Parameters:
        device_id: The ID of the device to get information for.

    HTTP Codes:
        * 200: OK
        * 404: Device not found
        * 500: Catchall processing error
    """
    logger.debug(_('processing request'), endpoint='/v3/info/<id>', id=device_id)

    return utils.http_json_response(
        await cmd.info(device_id),
    )


@v3.route('/read')
async def read(request):
    """Read data from devices which match the set of provided tags.

    Reading data is returned for only those devices which match all of the
    specified tags.

    Query Parameters:
        ns: The default namespace to use for specified tags without explicit namespaces.
            Only one default namespace may be specified. (default: ``default``)
        tags: The tags to filter devices on. If specifying multiple tags, they can
            be passed in as a comma-separated list, e.g. ``?tags=tag1,tag2,tag3``,
            or via multiple ``tags`` parameters, e.g. ``?tags=tag1&tags=tag2&tags=tag3``.

    HTTP Codes:
        * 200: OK
        * 400: Invalid parameter(s)
        * 500: Catchall processing error
    """
    logger.debug(_('processing request'), endpoint='/v3/read', pararms=request.args)

    return text('read')


@v3.route('/readcache')
async def read_cache(request):
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
    logger.debug(_('processing request'), endpoint='/v3/readcache', params=request.args)

    return text('readcache')


@v3.route('/read/<device_id>')
async def read_device(request, device_id):
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
    logger.debug(_('processing request'), endpoint='/v3/read/<id>', id=device_id)

    return text('read {id}')


@v3.route('/write/<device_id>', methods=['POST'])
async def async_write(request, device_id):
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
    logger.debug(_('processing request'), endpoint='/v3/write/<id>', id=device_id)

    return text('async write')


@v3.route('/write/wait/<device_id>', methods=['POST'])
async def sync_write(request, device_id):
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
    logger.debug(_('processing request'), endpoint='/v3/write/wait/<id>', id=device_id)

    return text('sync write')


@v3.route('/transaction')
async def transactions(request):
    """Get a list of all transactions currently being tracked by Synse Server.

    HTTP Codes:
        * 200: OK
        * 500: Catchall processing error
    """
    logger.debug(_('processing request'), endpoint='/v3/transaction')

    return text('transactions')


@v3.route('/transaction/<transaction_id>')
async def transaction(request, transaction_id):
    """Get the status of a write transaction.

    URI Parameters:
        transaction_id: The ID of the write transaction to get the status of.

    HTTP Codes:
        * 200: OK
        * 404: Transaction not found
        * 500: Catchall processing error
    """
    logger.debug(_('processing request'), endpoint='/v3/transaction/<id>', id=transaction_id)

    return text('transaction {id}')


@v3.route('/device/<device_id>', methods=['GET', 'POST'])
async def device(request, device_id):
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
    logger.debug(_('processing request'), endpoint='/v3/device/<id>', id=device_id)

    if request.method == 'GET':
        return read_device(request, device_id)

    else:
        return sync_write(request, device_id)
