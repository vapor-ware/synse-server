"""Command handler for the `test` route."""

from synse_server.scheme import TestResponse


async def test():
    """The handler for the Synse Server "test" API command.

    Returns:
        TestResponse: The "test" response scheme model.
    """
    return TestResponse()
