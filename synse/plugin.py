"""Management and access logic for configured plugin backends."""

import os
import stat

from synse import config, const, errors
from synse.i18n import _
from synse.log import logger
from synse.proto.client import register_client


class PluginManager(object):
    """Manager for all registered background plugins.

    Only a single instance of the PluginManager should be used. It is
    accessible from the `manager` class member of any instance of the
    `Plugin` class.
    """

    def __init__(self):
        self.plugins = {}

    def get(self, name):
        """Get a Plugin instance by name.

        Args:
            name (str): The name of the Plugin.

        Returns:
            Plugin: The Plugin instance with the matching name.
            None: The given name does not correspond to a known
                Plugin instance.
        """
        return self.plugins.get(name)

    def add(self, plugin):
        """Add a new Plugin to the manager.

        All plugins should be added to the Manager, since this is how they
        are accessed later. An error will be raised if a Plugin with the same
        name is already tracked by the manager.

        Args:
            plugin (Plugin): The plugin instance to add to the manager.

        Raises:
            errors.PluginStateError: The manager was not able to add the
                plugin either because the given object was not a plugin
                or a plugin with the same name is already being tracked.
        """
        if not isinstance(plugin, Plugin):
            raise errors.PluginStateError(
                _('Only Plugin instances can be added to the manager')
            )

        name = plugin.name
        if name in self.plugins:
            raise errors.PluginStateError(
                _('Plugin ("{}") already exists in the manager').format(name)
            )

        self.plugins[name] = plugin

    def remove(self, name):
        """Remove the plugin from the manager.

        If a specified name does not exist in the managed plugins dictionary,
        this will not fail, but it will log the event.

        Args:
            name (str): The name of the Plugin.
        """
        if name not in self.plugins:
            logger.debug(
                _('"{}" is not known to PluginManager - nothing to remove')
                .format(name)
            )
        else:
            del self.plugins[name]

    def purge(self, names):
        """Remove all of the specified Plugins from the manager.

        Args:
            names (list[str]): The names of the Plugins to remove.
        """
        for name in names:
            if name in self.plugins:
                del self.plugins[name]
        logger.debug(_('PluginManager purged plugins: {}').format(names))


class Plugin(object):
    """The Plugin object configures and controls access to a Synse Plugin
    via the Synse gRPC API.

    On initialization, all Plugin instances are registered with the
    PluginManager.

    Args:
        name (str): The name of the plugin.
        mode (str): The communication mode of the plugin. Currently,
            only 'tcp' and 'unix' modes are supported.
        address (str): The address of the plugin. The value for the
            address is dependent on the communication mode of the plugin.
            For 'unix', this would be the path to the unix socket. For
            'tcp', this would be the host[:port].
    """

    manager = None

    def __init__(self, name, address, mode):
        self.name = name
        self.mode = mode
        self.addr = address

        self._validate_mode()
        self.client = register_client(name, address, mode)

        # Register this instance with the manager.
        self.manager.add(self)

    def __str__(self):
        return '<Plugin ({}): {} {}>'.format(self.mode, self.name, self.addr)

    def _validate_mode(self):
        """Validate the plugin mode.

        Raises:
            errors.PluginStateError: The plugin mode is unsupported. This will
                also be raised if the mode is 'unix', but the socket does not
                exist.
        """
        if self.mode not in ['tcp', 'unix']:
            raise errors.PluginStateError(
                _('The given mode ({}) must be one of: tcp, unix').format(self.mode)
            )

        if self.mode == 'unix':
            if not os.path.exists(self.addr):
                raise errors.PluginStateError(
                    _('Unix socket ({}) does not exist').format(self.addr)
                )


# Create an instance of the PluginManager to use for all plugins
Plugin.manager = PluginManager()


def get_plugin(name):
    """Get the Plugin instance with the given name.

    Args:
        name (str): The name of the plugin.

    Returns:
        Plugin: The Plugin instance associated with the given name.
        None: The given name is not associated with a known plugin.
    """
    return Plugin.manager.get(name)


async def get_plugins():
    """Get all of the plugins registered with the manager.

    Yields:
        tuple: A tuple of plugin name and associated Plugin.
    """
    for k, v in Plugin.manager.plugins.items():
        yield k, v


def register_plugins():
    """Register all of the configured plugins.

    Plugins can either use a unix socket or TCP for communication. Unix
    socket based plugins will be detected from the presence of the socket
    file in a well-known directory, or via configuration. TCP based plugins
    will need to be made known to Synse Server via configuration.

    Upon initialization, the Plugin instances are automatically registered
    with the PluginManager.
    """
    unix = register_unix_plugins()
    tcp = register_tcp_plugins()

    diff = set(Plugin.manager.plugins) - set(unix + tcp)

    # Now that we have found all current plugins, we will want to clear out
    # any old plugins which may no longer be present.
    logger.debug(_('Plugins to purge from manager: {}').format(diff))
    Plugin.manager.purge(diff)

    logger.debug(_('Plugin registration complete'))


def register_unix_plugins():
    """Register the plugins that use a unix socket for communication.

    Unix plugins can be configured in a variety of ways:
      1.) Listed in the configuration file under plugin.unix
      2.) Via environment variable
      2.) Automatically, by placing the socket in the default socket directory

    Here, we will parse the configurations and the default socket directory,
    add them to the PluginManager, and return a unified list of all known
    unix-configured plugins.

    Returns:
        list[str]: The names of all plugins that were registered.
    """
    logger.debug(_('Registering plugins (unix)'))

    manager = Plugin.manager

    # Track the names of the plugins that have been registered.
    registered = []

    # First, register any plugins that are specified in the Synse Server
    # configuration (file, env).
    configured = config.options.get('plugin.unix', {})
    logger.debug(_('Unix plugins in configuration: {}').format(configured))
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
            sock_path = os.path.join(path, name + '.sock')
            logger.debug(_('Checking for socket: {}').format(sock_path))
            if not os.path.exists(sock_path):
                logger.debug(_('Checking for socket: {}').format(sock_path))
                sock_path = os.path.join(path, name)
                if not os.path.exists(sock_path):
                    logger.error(
                        _('Unable to find configured socket: {}[.sock]').format(sock_path)
                    )
                    continue

            # Check that the file is a socket
            if not stat.S_ISSOCK(os.stat(sock_path).st_mode):
                logger.warning(_('{} is not a socket - skipping').format(sock_path))
                continue

            # We have a plugin socket. If it already exists, there is nothing
            # to do; it is already registered. If it does not exist, we will
            # need to register it.
            if manager.get(name) is None:
                plugin = Plugin(name=name, address=sock_path, mode='unix')
                logger.debug(_('Created new plugin (unix): {}').format(plugin))
            else:
                logger.debug(
                    _('Unix Plugin "{}" already exists - will not re-register').format(name)
                )

            registered.append(name)

    # Now go through the default socket directory to pick up any other sockets
    # that may be set for automatic registration.
    if not os.path.exists(const.SOCKET_DIR):
        logger.debug(
            _('No default socket path found -- no plugins registered from {}')
            .format(const.SOCKET_DIR)
        )

    else:
        logger.debug(_('Registering plugins from default socket directory'))

        for item in os.listdir(const.SOCKET_DIR):
            logger.debug('  {}'.format(item))
            fqn = os.path.join(const.SOCKET_DIR, item)
            name, __ = os.path.splitext(item)  # pylint: disable=unused-variable

            # Check that the file is a socket
            if not stat.S_ISSOCK(os.stat(fqn).st_mode):
                logger.warning(_('{} is not a socket - skipping').format(fqn))
                continue

            # We have a plugin socket. If it already exists, there is nothing
            # to do; it is already registered. If it does not exist, we will
            # need to register it.
            if manager.get(name) is None:
                # A new plugin gets added to the manager on initialization.
                plugin = Plugin(name=name, address=fqn, mode='unix')
                logger.debug(_('Created new plugin (unix): {}').format(plugin))

                # Add the plugin to the Synse Server configuration. This will
                # allow a caller of the '/config' endpoint to see what plugins
                # are configured. Further, it can help with other processing that
                # might need the list of configured plugins.
                #
                # The value of `None` is used to indicate the default directory.
                config.options.set('plugin.unix.{}'.format(name), None)

            else:
                logger.debug(
                    _('Unix Plugin "{}" already exists - will not re-register').format(name)
                )

            registered.append(name)

    return list(set(registered))


def register_tcp_plugins():
    """Register the plugins that use TCP for communication.

    Return:
        list[str]: The names of all plugins that were registered.
    """
    logger.debug(_('Registering plugins (tcp)'))

    configured = config.options.get('plugin.tcp', {})
    logger.debug(_('TCP plugins in configuration: {}').format(configured))
    if not configured:
        return []

    manager = Plugin.manager

    # Track the names of all plugins that are registered.
    registered = []

    for name, address in configured.items():
        if manager.get(name) is None:
            # A new plugin gets added to the manager on initialization.
            plugin = Plugin(name=name, address=address, mode='tcp')
            logger.debug(_('Created new plugin (tcp): {}').format(plugin))
        else:
            logger.debug(
                _('TCP Plugin "{}" already exists - will not re-register').format(name)
            )

        registered.append(name)

    return list(set(registered))
