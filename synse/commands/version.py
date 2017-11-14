"""Command handler for the `version` route.
"""

from synse.scheme import VersionResponse


async def version():
    """The handler for the Synse Server "version" API command.

    Returns:
        VersionResponse: The "version" response scheme model.
    """
    return VersionResponse()
