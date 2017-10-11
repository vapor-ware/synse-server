"""

"""

import logging
import logging.config

from synse.config import LOGGING

logger = logging.getLogger('synse')


def setup_logger():
    """
    """
    logging.config.dictConfig(LOGGING)
    logger.setLevel(logging.DEBUG)
    logger.disabled = False
