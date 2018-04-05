"""Command handler for the `plugins` route.
"""

from synse import plugin
from synse.scheme.plugins import PluginsResponse


async def get_plugins():
    """The handler for the Synse Server "plugins" API command.

    Returns:
        PluginsResponse: The "plugins" response scheme model.
    """
    # register plugins. if no plugins exist, this will attempt to register
    # new ones. if plugins already exist, this will just ensure that all of
    # the tracked plugins are up to date.
    plugin.register_plugins()

    # Build a view of all the plugins registered with the plugin manager.
    # Here we take the element at index 1 because get_plugins returns a tuple
    # of (name, plugin) -- we are only interested in the plugin.
    plugins = [{
        'name': p[1].name,
        'network': p[1].mode,
        'address': p[1].addr
    } async for p in plugin.get_plugins()]

    return PluginsResponse(data=plugins)
