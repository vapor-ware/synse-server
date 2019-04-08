
import synse_server.config


async def config():
    """Generate the config response data.

    Returns:
        dict: A dictionary representation of the config response.
    """
    return {k: v for k, v in synse_server.config.options.config.items() if not k.startswith('_')}
