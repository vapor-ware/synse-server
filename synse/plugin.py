"""Management and access logic for configured plugin backends."""

import os
import stat

from synse import config, const, errors
from synse.discovery import kubernetes
from synse.i18n import _
from synse.log import logger
from synse.proto import client


class PluginManager(object):
    """Manager for all registered background plugins.

    Only a single instance of the PluginManager should be used. It is
    accessible from the `manager` class member of any instance of the
    `Plugin` class.
    """

    def __init__(self):
        self.plugins = {}

    def get(self, plugin_id):
        """Get a Plugin instance by ID.

        Args:
            plugin_id (str): The id of the Plugin.

        Returns:
            Plugin: The Plugin instance with the matching id.
            None: The given id does not correspond to a known
                Plugin instance.
        """
        return self.plugins.get(plugin_id)

    def get_by_address(self, address):
        """Get a Plugin instance by address.

        Args:
            address (str): The address of the Plugin.

        Returns:
            Plugin: The Plugin instance with the matching address.
            None: The given address does not correspond to a known
                Plugin instance.
        """
        for _, plugin in self.plugins.items():
            if plugin.address == address:
                return plugin
        return None

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

        plugin_id = plugin.id()
        if plugin_id in self.plugins:
            raise errors.PluginStateError(
                _('Plugin ("{}") already exists in the manager').format(plugin_id)
            )

        self.plugins[plugin_id] = plugin

    def remove(self, plugin_id):
        """Remove the plugin from the manager.

        If a specified name does not exist in the managed plugins dictionary,
        this will not fail, but it will log the event.

        Args:
            plugin_id (str): The id of the Plugin.
        """
        if plugin_id not in self.plugins:
            logger.debug(
                _('"{}" is not known to PluginManager - nothing to remove')
                .format(plugin_id)
            )
        else:
            del self.plugins[plugin_id]

    def purge(self, ids):
        """Remove all of the specified Plugins from the manager.

        Args:
            ids (list[str]): The ids of the Plugins to remove.
        """
        for plugin_id in ids:
            if plugin_id in self.plugins:
                del self.plugins[plugin_id]
        logger.debug(_('PluginManager purged plugins: {}').format(ids))


class Plugin(object):
    """The Plugin object models a Synse Plugin that has been registered with
    Synse Server. It holds the Plugin metadata as well as a reference to a client
    for communicating with the plugin via the Synse gRPC API.

    On initialization, all Plugin instances are registered with the PluginManager.

    Args:
        metadata (Metadata): The gRPC Metadata data for the Plugin.
        address (str): The address of the Plugin.
        plugin_client (client.PluginClient): The client for communicating with
            the Plugin.
    """

    manager = None

    # FIXME: remove address, get it from the client.
    def __init__(self, metadata, address, plugin_client):
        self.name = metadata.name
        self.maintainer = metadata.maintainer
        self.tag = metadata.tag
        self.description = metadata.description
        self.vcs = metadata.vcs
        self.version = metadata.version

        self.client = plugin_client
        self.address = address
        self.protocol = plugin_client.type

        # Register this instance with the manager.
        self.manager.add(self)

    def __str__(self):
        return '<Plugin ({}): {}@{}>'.format(self.tag, self.protocol, self.address)

    def id(self):
        """Get the ID of the plugin. The ID is a composite of the
        plugin's tag, mode, and address.

        Returns:
            string: The ID for the Plugin.
        """
        return '{}+{}@{}'.format(self.tag, self.protocol, self.address)


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
    # Register plugins from local config (file, env)
    unix = register_unix()
    tcp = register_tcp()

    # Get addresses of plugins to register via service discovery
    discovered = []
    addresses = kubernetes.discover()
    for address in addresses:
        plugin_id = register_plugin(address, 'tcp')
        if plugin_id is None:
            logger.error(_('Failed to register plugin with address: {}').format(address))
            continue
        discovered.append(plugin_id)

    diff = set(Plugin.manager.plugins) - set(unix + tcp + discovered)

    # Now that we have found all current plugins, we will want to clear out
    # any old plugins which may no longer be present.
    logger.debug(_('Plugins to purge from manager: {}').format(diff))
    Plugin.manager.purge(diff)

    logger.debug(_('Plugin registration complete'))


def register_plugin(address, protocol):
    """Register a plugin. If a plugin with the given address already exists,
    it will not be re-registered, but its ID will still be returned.

    If a plugin fails to register, None is returned.

    Args:
        address (str): The address of the plugin to register.
        protocol (str): The protocol that the plugin uses. This should
            be one of 'unix', 'tcp'.

    Returns:
        str: The ID of the plugin that was registered.
        None: The given address failed to resolve, so no plugin
            was registered.

    Raises:
        ValueError: An invalid protocol is specified. The protocol must
            be one of: 'unix', 'tcp'

    """
    plugin = Plugin.manager.get_by_address(address)
    if plugin:
        logger.debug(_('{} is already registered').format(plugin))
        return plugin.id()

    # The client does not exist, so we must register it. This means we need to
    # connect with it to (a) make sure its reachable, and (b) get its metadata
    # in order to properly create a new Plugin model for it.
    if protocol == 'tcp':
        plugin_client = client.PluginTCPClient(address)
    elif protocol == 'unix':
        plugin_client = client.PluginUnixClient(address)
    else:
        raise ValueError(_('Invalid protocol specified for registration: {}').format(protocol))

    try:
        status = plugin_client.test()
        if not status.ok:
            logger.warning(_('gRPC Test response was not OK: {}').format(address))
            return None
    except Exception as e:
        logger.warning(_('Failed to reach plugin at address {}: {}').format(address, e))
        return None

    # If we made it here, we were successful in establishing communication
    # with the plugin. Now, we should get its metainfo and create a Plugin
    # instance with it.
    try:
        meta = plugin_client.metainfo()
    except Exception as e:
        logger.warning(_('Failed to get plugin metadata at address {}: {}').format(address, e))
        return None

    plugin = Plugin(
        metadata=meta,
        address=address,
        plugin_client=plugin_client
    )

    logger.debug(_('Registered new plugin: {}').format(plugin))
    return plugin.id()


def register_tcp():
    """Register the plugins that use TCP for communication.

    Return:
        list[str]: The ids of all plugins that were registered.
    """
    logger.debug(_('Registering plugins (tcp)'))
    registered = []

    configured = config.options.get('plugin.tcp', [])
    if not configured:
        logger.debug(_('No plugin configurations for TCP'))
        return registered

    logger.debug(_('TCP plugin configuration: {}').format(configured))
    for address in configured:
        plugin_id = register_plugin(address, 'tcp')
        if plugin_id is None:
            logger.error(_('Failed to register plugin with address: {}').format(address))
            continue
        registered.append(plugin_id)

    return registered


def register_unix():
    """Register the plugins that use a unix socket for communication.

    Unix plugins can be configured in a variety of ways:
      1.) Listed in the configuration file under plugin.unix
      2.) Via environment variable
      2.) Automatically, by placing the socket in the default socket directory

    Here, we will parse the configurations and the default socket directory,
    add them to the PluginManager, and return a unified list of all known
    unix-configured plugins.

    Returns:
        list[str]: The ids of all plugins that were registered.
    """
    logger.debug(_('Registering plugins (unix)'))
    registered = []

    configured = config.options.get('plugin.unix', [])
    if not configured:
        logger.debug(_('No plugin configurations for unix'))

    logger.debug(_('unix plugin configuration: {}').format(configured))
    for address in configured:
        # The config here should be the path the the unix socket, which is our address.
        # First, check that the socket exists and that the address is a socket file.
        if not os.path.exists(address):
            logger.error(_('Socket {} not found').format(address))
            continue

        if not stat.S_ISSOCK(os.stat(address).st_mode):
            logger.error(_('{} is not a socket').format(address))
            continue

        plugin_id = register_plugin(address, 'unix')
        if plugin_id is None:
            logger.error(_('Failed to register plugin with address: {}').format(address))
            continue
        registered.append(plugin_id)

    # Now, go through the default socket directory and pick up any sockets that
    # may be set for automatic registration.
    if not os.path.exists(const.SOCKET_DIR):
        logger.debug(
            _('No default socket path found, no plugins will be registered from {}')
            .format(const.SOCKET_DIR)
        )
    else:
        logger.debug(_('Registering plugins from default socket directory'))

        for item in os.listdir(const.SOCKET_DIR):
            logger.debug('  {}'.format(item))
            address = os.path.join(const.SOCKET_DIR, item)

            # Check if the file is a socket
            if not stat.S_ISSOCK(os.stat(address).st_mode):
                logger.debug(_('{} is not a socket - skipping').format(address))
                continue

            plugin_id = register_plugin(address, 'unix')
            if plugin_id is None:
                logger.error(_('Failed to register plugin with address: {}').format(address))
                continue
            registered.append(plugin_id)

            # We want the plugins registered from this default directory to
            # be surfaced in the config, so we will add it there.
            if config.options.get('plugin.unix') is None:
                config.options.set('plugin.unix', [address])
            else:
                config.options.get('plugin.unix').append(address)

    return registered
