"""

"""

import datetime
import os
import stat

import aiocache
from sanic.exceptions import NotFound, ServerError
from sanic.response import text

from synse import errors
from synse.cache import get_location_device_map
from synse.config import AIOCACHE
from synse.const import BG_SOCKS
from synse.log import logger
from synse.proc import BGProc
from synse.response import json


async def get_device_uid(rack, board, device):
    """ Get the internal UID for a device which matches the provided rack,
    board, and device descriptors.

    Args:
        rack (str):
        board (str):
        device (str):

    Returns:
        str:
        None:
    """
    ld_map = await get_location_device_map()
    return ld_map.get(rack, {}).get(board, {}).get(device)


def disable_favicon(app):
    """ Return empty response when looking for favicon.

    Args:
        app: the Sanic application to add the route to.
    """
    @app.route('/favicon.ico')
    def favicon(*_):
        return text('')


# FIXME - should probably move to `cache` module?
def configure_cache():
    """ Set the configuration for the asynchronous cache used by Synse.
    """
    logger.debug('CONFIGURING CACHE: {}'.format(AIOCACHE))
    aiocache.caches.set_config(AIOCACHE)


# FIXME - maybe this moves to the 'proc' module?
def register_background_processes():
    """ Find the sockets for the configured background processes.

    Upon initialization, the BGProc instances are automatically registered
    with the ProcManager.
    """
    logger.debug('Registering background processes')
    if not os.path.exists(BG_SOCKS):
        raise ValueError(
            '{} does not exist - cannot get background process '
            'sockets.'.format(BG_SOCKS)
        )

    logger.debug('sock dir exists')
    for item in os.listdir(BG_SOCKS):
        logger.debug('  {}'.format(item))
        fqn = os.path.join(BG_SOCKS, item)
        name, _ = os.path.splitext(item)

        if stat.S_ISSOCK(os.stat(fqn).st_mode):
            bgproc = BGProc(name=name, sock=fqn)
            logger.debug('Found bgproc: {}'.format(bgproc))
        else:
            logger.debug('not a socket.. {}'.format(fqn))

    logger.debug('done registering')


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
