"""

"""

import datetime

import aiocache
from sanic.exceptions import NotFound, ServerError
from sanic.response import text

from synse import errors
from synse.config import AIOCACHE
from synse.log import logger
from synse.response import json


def disable_favicon(app):
    """Return empty response when looking for favicon.

    Args:
        app: The Sanic application to add the route to.
    """
    @app.route('/favicon.ico')
    def favicon(*_):
        return text('')


def composite(rack, board, device):
    """Create a composite string out of a rack, board, and device.

    This can be used to uniquely identify a device across all racks.

    Args:
        rack (str): The rack associated with the device.
        board (str): The board associated with the device.
        device (str): The ID of the device.

    Returns:
        str: A composite of the input strings.
    """
    return '-'.join([rack, board, device])


# FIXME - should probably move to `cache` module?
def configure_cache():
    """Set the configuration for the asynchronous cache used by Synse.
    """
    logger.debug('CONFIGURING CACHE: {}'.format(AIOCACHE))
    aiocache.caches.set_config(AIOCACHE)


# FIXME - this probably doesn't belong here, but putting it here for now.
def register_error_handling(app):
    """

    Args:
        app ():
    """

    @app.exception(NotFound)
    def err_404(request, exception):
        """
        """
        err = {
            'http_code': 404,
            'error_id': errors.URL_NOT_FOUND,
            'description': errors.codes[errors.URL_NOT_FOUND],
            'timestamp': str(datetime.datetime.utcnow()),
            'context': str(exception)
        }

        return json(err, status=404)

    @app.exception(ServerError)
    def err_500(request, exception):
        """
        """
        if hasattr(exception, 'error_id'):
            error_id = exception.error_id
        else:
            error_id = errors.UNKNOWN

        err = {
            'http_code': 500,
            'error_id': error_id,
            'description': errors.codes[error_id],
            'timestamp': str(datetime.datetime.utcnow()),
            'context': str(exception)
        }

        return json(err, status=500)
