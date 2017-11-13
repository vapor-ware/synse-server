"""Management and access logic for configured plugin backends.
"""

import os
import stat

from synse.const import BG_SOCKS
from synse.log import logger
from synse.proto.client import get_client


class PluginManager(object):
    """Manager for registered background plugins.
    """

    def __init__(self):
        self.plugins = {}

    def get(self, name):
        """Get the named Plugin instance by name.

        Args:
            name (str): The name of the Plugin to get.

        Returns:
            Plugin: The Plugin instance with the matching name.
            None: if the given name does not correspond to a managed
                Plugin instance.
        """
        return self.plugins.get(name)

    def add(self, plugin):
        """Add a new Plugin to the managed dictionary.

        Args:
            plugin (Plugin): The background plugin object to
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

    def remove(self, name):
        """Remove the record for the Plugin with the given name.

        If a specified name does not exist in the managed plugins dictionary,
        this will not fail, but it will log the event.

        Args:
            name (str): The name of the Plugin to remove.
        """
        if name not in self.plugins:
            logger.debug('"{}" is not known to PluginManager - will not remove.'.format(name))
        else:
            del self.plugins[name]


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


def register_plugins():
    """Find the sockets for the configured plugins.

    Upon initialization, the Plugin instances are automatically registered
    with the PluginManager.
    """
    logger.debug('Registering background plugins')
    if not os.path.exists(BG_SOCKS):
        raise ValueError(
            '{} does not exist - cannot get background plugin '
            'sockets.'.format(BG_SOCKS)
        )

    logger.debug('sock dir exists')

    manager = Plugin.manager

    # track the names of all plugins that were found.
    found = []

    for item in os.listdir(BG_SOCKS):
        logger.debug('  {}'.format(item))
        fqn = os.path.join(BG_SOCKS, item)
        name, _ = os.path.splitext(item)

        if stat.S_ISSOCK(os.stat(fqn).st_mode):
            found.append(name)

            # we have a plugin socket. if it already exists, there is nothing
            # to do; it is already registered. if it does not exist, we will
            # need to register it.
            if manager.get(name) is None:
                # a new plugin gets added to the manager on initialization.
                plugin = Plugin(name=name, sock=fqn)
                logger.debug('Found plugin: {}'.format(plugin))

        else:
            logger.debug('not a socket.. {}'.format(fqn))

    # now that we have found all current plugins, we will want to clear out
    # any old plugins which may no longer be present.
    diff = set(manager.plugins) - set(found)
    logger.debug('Plugins to be removed from manager: {}'.format(diff))
    for old in diff:
        manager.remove(old)

    logger.debug('done registering')
