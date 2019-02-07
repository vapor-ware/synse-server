"""Synse Server HTTP API."""

from sanic import Blueprint
from sanic.response import text

from synse_server.log import logger

# Blueprint for the Synse core (version-less) routes.
core = Blueprint('core-http')

# Blueprint for the Synse v3 HTTP API.
v3 = Blueprint('v3-http', version='v3')


@core.route('/test')
async def test(request):
    """"""
    return text('test')


@core.route('/version')
async def version(request):
    """"""
    return text('version')


@v3.route('/config')
async def config(request):
    """"""
    return text('config')


@v3.route('/plugin')
async def plugins(request):
    """"""
    return text('plugin')


@v3.route('/plugin/<plugin_id>')
async def plugin(request, plugin_id):
    """"""
    return text('plugin {id}')


@v3.route('/plugin/health')
async def plugin_health(request):
    """"""
    return text('plugin health')


@v3.route('/scan')
async def scan(request):
    """"""
    return text('scan')


@v3.route('/tags')
async def tags(request):
    """"""
    return text('tags')


@v3.route('/info/<device_id>')
async def info(request, device_id):
    """"""
    return text('info')


@v3.route('/read')
async def read(request):
    """"""
    return text('read')


@v3.route('/readcache')
async def read_cache(request):
    """"""
    return text('readcache')


@v3.route('/read/<device_id>')
async def read_device(request, device_id):
    """"""
    return text('read {id}')


@v3.route('/write/<device_id>')
async def async_write(request, device_id):
    """"""
    return text('async write')


@v3.route('/write/wait/<device_id>')
async def sync_write(request, device_id):
    """"""
    return text('sync write')


@v3.route('/transaction')
async def transactions(request):
    """"""
    return text('transactions')


@v3.route('/transaction/<transaction_id>')
async def transaction(request, transaction_id):
    """"""
    return text('transaction {id}')


@v3.route('/device/<device_id>')
async def device(request, device_id):
    """"""
    return text('device')
