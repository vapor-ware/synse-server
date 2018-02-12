"""Command handler for the `plugins` route.
"""

from synse import plugin
from synse.scheme.plugins import PluginsResponse


async def get_plugins():
    """The handler for the Synse Server "plugins" API command.

    Returns:
        PluginsResponse: The "plugins" response scheme model.
    """
    # List of configured plugins
    plugins = []

    # Get the plugins generators
    plugins_generators = plugin.get_plugins()
    for item in plugins_generators:
        plugins.append({
            'name': item[1].name,
            'network': item[1].mode,
            'address': item[1].addr
        })

    return PluginsResponse(data=plugins)
