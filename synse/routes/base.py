"""

"""

from sanic import Blueprint

from synse import commands

bp = Blueprint(__name__, url_prefix='/synse')


@bp.route('/test')
async def test_route(request):
    """ Endpoint to test whether the service is up and reachable.

    Args:
        request:
    """
    response = await commands.test()
    return response.to_json()


@bp.route('/version')
async def version_route(request):
    """ Endpoint to get the API version of the service.

    Args:
        request:
    """
    response = await commands.version()
    return response.to_json()
