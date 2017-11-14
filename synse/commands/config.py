"""Command handler for the `config` route.
"""

from synse.scheme.config import ConfigResponse


async def config():
    """

    """
    return ConfigResponse()
