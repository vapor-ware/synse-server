"""Command handler for the `config` route."""

from synse.scheme.config import ConfigResponse


async def config():
    """The handler for the Synse Server "config" API command.

    Returns:
        ConfigResponse: The "config" response scheme model.
    """
    return ConfigResponse()
