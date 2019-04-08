
from synse_server import utils


async def test():
    """Generate the test response data.

    Returns:
        dict: A dictionary representation of the test response.
    """
    return {
        'status': 'ok',
        'timestamp': utils.rfc3339now(),
    }
