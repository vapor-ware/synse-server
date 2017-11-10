"""Command handler for the `test` route.
"""

from synse.scheme import TestResponse


async def test():
    """
    """
    return TestResponse()
