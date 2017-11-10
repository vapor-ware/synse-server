"""Management and access logic for configured plugin backends.
"""

import os

from synse.proto.client import get_client


class PluginManager(object):
    """Manager for registered background plugins.
    """

    def __init__(self):
        self.plugins = {}

    def get(self, name):
        """Get the named Plugin instance by name.

        Args:
            name (str): the name of the Plugin to get.

        Returns:
            Plugin: the Plugin instance with the matching name.
            None: if the given name does not correspond to a managed
                Plugin instance.
        """
        return self.plugins.get(name)

    def add(self, plugin):
        """Add a new Plugin to the managed dictionary.

        Args:
            plugin (Plugin): the background plugin object to
                add to the managed dictionary.
        """
        if not isinstance(plugin, Plugin):
            raise ValueError(
                'Only Plugin instances can be added to the manager.'
            )

        name = plugin.name
        if name in self.plugins:
            raise ValueError(
                'The given Plugin ("{}") already exists in the managed '
                'dictionary.'.format(name)
            )

        self.plugins[name] = plugin


class Plugin(object):
    """Class which holds the relevant information for a configured
    plugin process for Synse.
    """
    manager = None

    def __init__(self, name, sock):
        """ Constructor for the Plugin object.

        Args:
            name (str): the name of the plugin. this is derived
                from the name of the socket.
            sock (str): the path to the socket.
        """
        if not os.path.exists(sock):
            raise ValueError('The given socket ({}) must exist.'.format(sock))
        self.sock = sock
        self.name = name
        self.client = get_client(name)

        # register this instance with the manager.
        self.manager.add(self)

    def __str__(self):
        return '<Plugin: {} {}>'.format(self.name, self.sock)


Plugin.manager = PluginManager()


def get_plugin(name):
    """Get the model for the plugin with the given name.

    Args:
        name (str): the name of the plugin.

    Returns:
        Plugin: the plugin model associated with the given name.
        None: if the given name is not associated with a known plugin.
    """
    return Plugin.manager.get(name)


def get_plugins():
    """Get all of the managed plugins.

    Yields:
        tuple: a tuple of plugin name and associated Plugin.
    """
    for k, v in Plugin.manager.plugins.items():
        yield k, v
