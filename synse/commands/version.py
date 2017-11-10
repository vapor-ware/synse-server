"""Command handler for the `version` route.
"""

from synse.scheme import VersionResponse


async def version():
    """
    """
    return VersionResponse()
