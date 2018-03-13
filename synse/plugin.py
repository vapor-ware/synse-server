"""Management and access logic for configured plugin backends.
"""

import os
import stat

from synse import config, const, errors
from synse.i18n import gettext
from synse.log import logger
from synse.proto.client import register_client


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
            None: The given name does not correspond to a managed
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
            raise errors.PluginStateError(
                gettext('Only Plugin instances can be added to the manager.')
            )

        name = plugin.name
        if name in self.plugins:
            raise errors.PluginStateError(
                gettext('Plugin ("{}") already exists in the manager.').format(name)
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
            logger.debug(
                gettext('"{}" is not known to PluginManager - nothing to remove.')
                .format(name)
            )
        else:
            del self.plugins[name]

    def purge(self, names):
        """Remove all of the specified tracked Plugins.

        Args:
            names (list[str]): The names of the Plugins to remove.
        """
        for name in names:
            if name in self.plugins:
                del self.plugins[name]
        logger.debug(gettext('PluginManager purged: {}').format(names))


class Plugin(object):
    """Class which holds the relevant information for a configured
    plugin process for Synse.
    """
    manager = None

    def __init__(self, name, address, mode):
        """Constructor for the Plugin object.

        Args:
            name (str): The name of the plugin. This is derived
                from the name of the socket.
            mode (str): The communication mode of the plugin. Currently,
                only 'tcp' and 'unix' are supported.
            address (str): The address of the plugin. The value for the
                address is dependent on the communication mode of the
                plugin.
        """
        self.name = name
        self.mode = mode
        self.addr = address

        self._validate_mode()
        self.client = register_client(name, address, mode)

        # register this instance with the manager.
        self.manager.add(self)

    def __str__(self):
        return '<Plugin ({}): {} {}>'.format(self.mode, self.name, self.addr)

    def _validate_mode(self):
        """Validate the plugin mode."""
        if self.mode not in ['tcp', 'unix']:
            raise errors.PluginStateError(
                gettext('The given mode ({}) must be one of: tcp, unix').format(self.mode)
            )

        if self.mode == 'unix':
            if not os.path.exists(self.addr):
                raise errors.PluginStateError(
                    gettext('Unix socket ({}) does not exist.').format(self.addr)
                )


Plugin.manager = PluginManager()


def get_plugin(name):
    """Get the model for the plugin with the given name.

    Args:
        name (str): The name of the plugin.

    Returns:
        Plugin: The plugin model associated with the given name.
        None: The given name is not associated with a known plugin.
    """
    return Plugin.manager.get(name)


async def get_plugins():
    """Get all of the managed plugins.

    Yields:
        tuple: A tuple of plugin name and associated Plugin.
    """
    for k, v in Plugin.manager.plugins.items():
        yield k, v


def register_plugins():
    """Register all of the configured plugins.

    Plugins can either use a unix socket for communication or TCP. Unix
    socket based plugins will be detected from the presence of the socket
    file in a well-known directory. TCP based plugins will need to be made
    known to Synse Server by environment variables.

    Upon initialization, the Plugin instances are automatically registered
    with the PluginManager.
    """
    unix = register_unix_plugins()
    tcp = register_tcp_plugins()

    diff = set(Plugin.manager.plugins) - set(unix + tcp)

    # now that we have found all current plugins, we will want to clear out
    # any old plugins which may no longer be present.
    logger.debug(gettext('Plugins to be removed from manager: {}').format(diff))
    Plugin.manager.purge(diff)

    logger.debug(gettext('done registering plugins'))


def register_unix_plugins():
    """Register the plugins that use a unix socket for communication.

    Unix plugins can be configured two ways:
      1.) Listed in the configuration file under plugin.unix
      2.) Automatically by existing in the default socket directory

    Here, we will parse both the configuration and the default socket
    directory and return a unified list of all known unix-configured
    plugins.

    Returns:
        list[str]: The names of all plugins that were registered.
    """
    logger.debug(gettext('Registering plugins (unix)'))

    manager = Plugin.manager

    # track the names of the plugins that have been registered
    registered = []

    # First, register any plugins that are defined in the Synse Server
    # configuration.
    configured = config.options.get('plugin.unix', {})
    logger.debug('configured unix plugins: {}'.format(configured))
    if configured:
        for name, path in configured.items():
            # If the user wants to use the default configuration directory,
            # they can specify something like
            #
            #   plugins:
            #       unix:
            #           plugin_name:
            #
            # This will give us a 'name' here of 'plugin_name' and a 'path'
            # of None.
            if path is None:
                path = const.SOCKET_DIR

            # Check for both 'plugin_name' and 'plugin_name.sock'
            sock_path = os.path.join(path, name, '.sock')
            logger.debug('checking for socket: {}'.format(sock_path))
            if not os.path.exists(sock_path):
                logger.debug('checking for socket: {}'.format(sock_path))
                sock_path = os.path.join(path, name)
                if not os.path.exists(sock_path):
                    logger.error('could not find configured socket: {}[.sock]'.format(sock_path))
                    continue

            if not stat.S_ISSOCK(os.stat(sock_path).st_mode):
                logger.error('{} is not a socket, will not register'.format(sock_path))
                continue

            # we have a plugin socket. if it already exists, there is nothing
            # to do; it is already registered. if it does not exist, we will
            # need to register it.
            if manager.get(name) is None:
                plugin = Plugin(name=name, address=sock_path, mode='unix')
                logger.debug(gettext('Created new plugin (unix): {}').format(plugin))
            else:
                logger.info(
                    gettext('plugin "{}" already exists - will not re-register (unix)').format(name)
                )

            registered.append(name)

    # Now go through the default socket directory to pick up any other sockets
    # that may be set for automatic registration.
    if not os.path.exists(const.SOCKET_DIR):
        logger.debug(
            gettext('default socket path does not exist, no plugins registered from {}')
            .format(const.SOCKET_DIR)
        )

    else:
        logger.debug(gettext('socket dir exists'))

        for item in os.listdir(const.SOCKET_DIR):
            logger.debug('  {}'.format(item))
            fqn = os.path.join(const.SOCKET_DIR, item)
            name, _ = os.path.splitext(item)

            if stat.S_ISSOCK(os.stat(fqn).st_mode):
                # we have a plugin socket. if it already exists, there is nothing
                # to do; it is already registered. if it does not exist, we will
                # need to register it.
                if manager.get(name) is None:
                    # a new plugin gets added to the manager on initialization.
                    plugin = Plugin(name=name, address=fqn, mode='unix')
                    logger.debug(gettext('Created new plugin (unix): {}').format(plugin))

                    # add the plugin to the Synse Server configuration. this will
                    # allow a caller of the '/config' endpoint to see what plugins
                    # are configured. further, it can help with other processing that
                    # might need the list of configured plugins.
                    #
                    # The value of `None` is used to indicate the default directory.
                    config.options.set('plugin.unix.{}'.format(name), None)

                else:
                    logger.info(
                        gettext('plugin "{}" already exists - will not re-register (unix)')
                        .format(name)
                    )
                registered.append(name)

            else:
                logger.debug(gettext('file is not a socket.. {}').format(fqn))

    return list(set(registered))


def register_tcp_plugins():
    """Register the plugins that use TCP for communication.

    Return:
        list[str]: The names of all plugins that were registered.
    """
    logger.debug(gettext('Registering plugins (tcp)'))

    configured = config.options.get('plugin.tcp', {})
    logger.debug('configured tcp plugins: {}'.format(configured))
    if not configured:
        logger.debug(gettext('found no plugins configured for tcp'))
        return []

    manager = Plugin.manager

    # track the names of all plugins that are registered.
    registered = []

    for name, address in configured.items():
        registered.append(name)
        if manager.get(name) is None:
            # a new plugin gets added to the manager on initialization.
            plugin = Plugin(name=name, address=address, mode='tcp')
            logger.debug(gettext('Created new plugin (tcp): {}').format(plugin))
        else:
            logger.info(
                gettext('plugin "{}" already exists - will not re-register (tcp)').format(name)
            )

    return list(set(registered))
