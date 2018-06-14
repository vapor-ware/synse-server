"""Management and access logic for configured plugin backends."""

import os
import stat

from synse import config, const, errors
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
        client (client.PluginClient): The client for communicating with
            the Plugin.
    """

    manager = None

    def __init__(self, metadata, address, client):
        self.name = metadata.name
        self.maintainer = metadata.maintainer
        self.tag = metadata.tag
        self.description = metadata.description
        self.vcs = metadata.vcs
        self.version = metadata.version

        self.client = client
        self.address = address
        self.mode = client.type

        # Register this instance with the manager.
        self.manager.add(self)

    def __str__(self):
        return '<Plugin ({}): {}@{}>'.format(self.tag, self.mode, self.address)

    def id(self):
        """Get the ID of the plugin. The ID is a composite of the
        plugin's tag, mode, and address.

        Returns:
            string: The ID for the Plugin.
        """
        return '{}+{}@{}'.format(self.tag, self.mode, self.address)


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
    unix = register_unix()
    tcp = register_tcp()

    diff = set(Plugin.manager.plugins) - set(unix + tcp)

    # Now that we have found all current plugins, we will want to clear out
    # any old plugins which may no longer be present.
    logger.debug(_('Plugins to purge from manager: {}').format(diff))
    Plugin.manager.purge(diff)

    logger.debug(_('Plugin registration complete'))


# FIXME (etd): a lot of the logic below can be cleaned up and consolidated.

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

    manager = Plugin.manager

    for address in configured:
        # The config here should be the address (host[:port])
        plugin = manager.get_by_address(address)
        if plugin:
            logger.debug(_('TCP plugin "{}" is already registered').format(plugin))
            registered.append(plugin.id())
            continue

        # The plugin has not already been registered, so we must try registering
        # it now. First, we'll need to create a client to check that the plugin
        # is reachable.

        plugin_client = client.PluginTCPClient(address)

        try:
            resp = plugin_client.test()
            if not resp.ok:
                raise errors.InternalApiError('gRPC Test response status was not "ok"')
        except Exception as e:
            logger.error(_('Failed to reach plugin at tcp {}: {}').format(address, e))
            continue

        # Now, we can communicate with the plugin, so we should get its metainfo
        # so we can create a Plugin instance for it.
        try:
            meta = plugin_client.metainfo()
        except Exception as e:
            logger.error(_('Failed to get plugin metadata at tcp {}: {}').format(address, e))
            continue

        plugin = Plugin(
            metadata=meta,
            address=address,
            client=plugin_client
        )

        logger.debug(_('Registered new plugin: {}').format(plugin))
        registered.append(plugin.id())

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
        return registered

    logger.debug(_('unix plugin configuration: {}').format(configured))

    manager = Plugin.manager

    for address in configured:
        # The config here should be the path the the unix socket, which is our address.
        # First, check that the socket exists and that the address is a socket file.
        if not os.path.exists(address):
            logger.error(_('Socket {} not found').format(address))
            continue

        if not stat.S_ISSOCK(os.stat(address).st_mode):
            logger.error(_("{} is not a socket").format(address))
            continue

        plugin = manager.get_by_address(address)
        if plugin:
            logger.debug(_('unix plugin "{}" is already registered').format(plugin))
            registered.append(plugin.id())
            continue

        # The plugin has not already been registered, so we must try registering
        # it now. First, we'll need to create a client to check that the plugin
        # is reachable.

        plugin_client = client.PluginUnixClient(address)

        try:
            resp = plugin_client.test()
            if not resp.ok:
                raise errors.InternalApiError('gRPC Test response status was not "ok"')
        except Exception as e:
            logger.error(_('Failed to reach plugin at unix {}: {}').format(address, e))
            continue

        # Now, we can communicate with the plugin, so we should get its metainfo
        # so we can create a Plugin instance for it.
        try:
            meta = plugin_client.metainfo()
        except Exception as e:
            logger.error(_('Failed to get plugin metadata at unix {}: {}').format(address, e))
            continue

        plugin = Plugin(
            metadata=meta,
            address=address,
            client=plugin_client
        )

        logger.debug(_('Registered new plugin: {}').format(plugin))
        registered.append(plugin.id())

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

            plugin = manager.get_by_address(address)
            if plugin:
                logger.debug(_('unix plugin "{}" is already registered').format(plugin))
                registered.append(plugin.id())
                continue

            # The plugin has not already been registered, so we must try registering
            # it now. First, we'll need to create a client to check that the plugin
            # is reachable.

            plugin_client = client.PluginUnixClient(address)

            try:
                resp = plugin_client.test()
                if not resp.ok:
                    raise errors.InternalApiError('gRPC Test response status was not "ok"')
            except Exception as e:
                logger.error(_('Failed to reach plugin at unix {}: {}').format(address, e))
                continue

            # Now, we can communicate with the plugin, so we should get its metainfo
            # so we can create a Plugin instance for it.
            try:
                meta = plugin_client.metainfo()
            except Exception as e:
                logger.error(_('Failed to get plugin metadata at unix {}: {}').format(address, e))
                continue

            plugin = Plugin(
                metadata=meta,
                address=address,
                client=plugin_client
            )

            logger.debug(_('Registered new plugin: {}').format(plugin))
            registered.append(plugin.id())

            # We want the plugins registered from this default directory to
            # be surfaced in the config, so we will add it there.
            config.options.get('plugin.unix').append(address)

    return registered
