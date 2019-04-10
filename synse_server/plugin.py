"""Management and access logic for configured plugin backends."""

from synse_grpc import client, utils

from synse_server import config, errors
from synse_server.discovery import kubernetes
from synse_server.i18n import _
from synse_server.log import logger


class PluginManager:
    """A manager for plugins registered with the Synse Server instance.

    The PluginManager state is kept as a class member, so all instances
    of the manager should operate on the same plugin state. The PluginManager
    is also iterable, where iterating over the manager will provide the
    snapshot of currently registered plugins.
    """

    plugins = {}

    def __iter__(self):
        self._snapshot = list(self.plugins.values())
        self._idx = 0
        return self

    def __next__(self):
        if self._idx >= len(self._snapshot):
            raise StopIteration

        plugin = self._snapshot[self._idx]
        self._idx += 1
        return plugin

    def get(self, plugin_id):
        """Get a ``Plugin`` by ID.

        Args:
            plugin_id (str): The ID of the plugin.

        Returns:
            Plugin | None: The plugin with the matching ID. If the given ID
            is not associated with a registered plugin, None is returned.
        """
        return self.plugins.get(plugin_id)

    def register(self, address, protocol):
        """Register a new Plugin with the manager.

        With the provided address and communication protocol, the manager
        will attempt to establish communication with the plugin to get its
        metadata. If successful, it will generate a new Plugin instance for
        the plugin and register it in the manager state.

        Args:
            address (str): The address of the plugin to register.
            protocol (str): The protocol that the plugin uses. This must be
                one of: 'unix', 'tcp'.

        Returns:
            str: The ID of the plugin that was registered.

        Raises:
            errors.ServerError: A plugin with the same ID is already registered.
        """
        # Prior to registering the plugin, we need to get the plugin metadata
        # and ensure that we can connect to the plugin.
        c = client.PluginClientV3(address, protocol)
        meta = c.metadata()
        ver = c.version()

        plugin = Plugin(
            info=utils.to_dict(meta),
            version=utils.to_dict(ver),
            client=c,
        )

        if plugin.id in self.plugins:
            raise errors.ServerError(
                _(f'plugin with id "{plugin.id}" already exists')
            )

        self.plugins[plugin.id] = plugin

        logger.debug(_('registered plugin'), id=plugin.id, tag=plugin.tag)
        return plugin.id

    @classmethod
    def load(cls):
        """Load plugins from configuration.

        Returns:
            list[tuple[str, str]]: A list of plugin configuration tuples where the
            first element is the plugin address and the second element is the protocol.
        """
        logger.info(_('loading plugins from configuration'))
        configs = []

        # Get plugin configs for TCP-configured plugins
        cfg_tcp = config.options.get('plugin.tcp', [])
        for address in cfg_tcp:
            logger.debug(_('plugin from config'), mode='tcp', address=address)
            configs.append((address, 'tcp'))

        # Get plugin configs for Unix socket-configured plugins
        cfg_unix = config.options.get('plugin.unix', [])
        for address in cfg_unix:
            logger.debug(_('plugin from config'), mode='unix', address=address)
            configs.append((address, 'unix'))

    @classmethod
    def discover(cls):
        """Discover plugins via the supported discovery methods.

        Currently, plugin discovery is supported by kubernetes service endpoints.

        Returns:
            list[tuple[str, str]]: A list of plugin configuration tuples where the
            first element is the plugin address and the second element is the protocol.
        """
        configs = []

        addresses = kubernetes.discover()
        for address in addresses:
            configs.append((address, 'tcp'))

        return configs

    def purge(self, ids):
        """Purge the plugins with the specified IDs from the manager.

        If a specified ID does not correspond to a tracked plugin, it is
        ignored.

        Args:
            ids (iterable[str]): The IDs of the plugins to remove.
        """
        for plugin_id in ids:
            if plugin_id in self.plugins:
                logger.debug(_('purging plugin from manager'), plugin=plugin_id)
                del self.plugins[plugin_id]

    def update(self):
        """Update the manager's tracked plugins."""

        logger.debug(_('updating plugin manager'))

        # Make a copy of the currently registered plugins. This is needed prior
        # to any refreshing so we can later determine which plugins are stale
        # and should be purged.
        pre_update = set(self.plugins.keys())

        plugins = self.load() + self.discover()
        registered = set()
        for address, protocol in plugins:
            try:
                pid = self.register(address, protocol)
            except Exception as e:
                logger.warning(
                    _('failed to register plugin'), address=address, protocol=protocol, error=e
                )
                continue
            else:
                registered.add(pid)

        # Get the difference between the set of plugins that were registered
        # before and the set of plugins that were registered now. Anything in
        # that difference is either no longer configured, or is not responding,
        # so it should be removed from the tracked plugins. It may be added back
        # in a future update if it becomes responsive again.
        # TODO (etd): Is this still the desired behavior? It seems like it may not
        #   be given that we wouldn't want devices popping in and out of existence.
        #   Its probably better to fail with a potentially intermittent "could not
        #   connect" error than a potentially intermittent "device not found" error,
        #   especially considering we want static routes for devices...
        diff = pre_update - registered
        self.purge(diff)

        logger.debug(_('plugin manager update complete'), plugin_count=len(self.plugins))


# A module-level instance of the plugin manager. This makes it easier to use
# the manager in various places, without having to initialize a new instance.
manager = PluginManager()


class Plugin:
    """Plugin stores the metadata for a registered plugin along with a client
    for communicating with the plugin via the Synse gRPC API.

    Generally, plugins are looked up by ID as each device will specify which
    plugin owns it via the plugin ID. Plugin IDs are generated by the plugin.

    Args:
        info (dict): A dictionary containing the metadata for the associated
            plugin.
        version (dict): A dictionary containing the version information
            for the associated plugin.
        client (client.PluginClientV3): The Synse v3 gRPC client used to
            communicate with the plugin.
    """

    def __init__(self, info, version, client):
        self.client = client

        self.address = self.client.get_address()
        self.protocol = self.client.protocol

        self.metadata = info
        self.version = version

        self.tag = info['tag']  # required
        self.id = info['id']  # required

    def __str__(self):
        return f'<Plugin ({self.tag}): {self.id}>'


# class PluginManager:
#     """Manager for all registered background plugins.
#
#     Only a single instance of the PluginManager should be used. It is
#     accessible from the `manager` class member of any instance of the
#     `Plugin` class.
#     """
#
#     def __init__(self):
#         self.plugins = {}
#
#     def get(self, plugin_id):
#         """Get a Plugin instance by ID.
#
#         Args:
#             plugin_id (str): The id of the Plugin.
#
#         Returns:
#             Plugin: The Plugin instance with the matching id.
#             None: The given id does not correspond to a known
#                 Plugin instance.
#         """
#         return self.plugins.get(plugin_id)
#
#     def get_by_address(self, address):
#         """Get a Plugin instance by address.
#
#         Args:
#             address (str): The address of the Plugin.
#
#         Returns:
#             Plugin: The Plugin instance with the matching address.
#             None: The given address does not correspond to a known
#                 Plugin instance.
#         """
#         for __, plugin in self.plugins.items():
#             if plugin.address == address:
#                 return plugin
#         return None
#
#     def add(self, plugin):
#         """Add a new Plugin to the manager.
#
#         All plugins should be added to the Manager, since this is how they
#         are accessed later. An error will be raised if a Plugin with the same
#         name is already tracked by the manager.
#
#         Args:
#             plugin (Plugin): The plugin instance to add to the manager.
#
#         Raises:
#             errors.PluginStateError: The manager was not able to add the
#                 plugin either because the given object was not a plugin
#                 or a plugin with the same name is already being tracked.
#         """
#         if not isinstance(plugin, Plugin):
#             raise errors.ServerError(
#                 _('Only Plugin instances can be added to the manager')
#             )
#
#         plugin_id = plugin.id()
#         if plugin_id in self.plugins:
#             raise errors.ServerError(
#                 _('Plugin ("{}") already exists in the manager').format(plugin_id)
#             )
#
#         self.plugins[plugin_id] = plugin
#
#     def remove(self, plugin_id):
#         """Remove the plugin from the manager.
#
#         If a specified name does not exist in the managed plugins dictionary,
#         this will not fail, but it will log the event.
#
#         Args:
#             plugin_id (str): The id of the Plugin.
#         """
#         if plugin_id not in self.plugins:
#             logger.debug(
#                 _('"{}" is not known to PluginManager - nothing to remove')
#                 .format(plugin_id)
#             )
#         else:
#             del self.plugins[plugin_id]
#
#     def purge(self, ids):
#         """Remove all of the specified Plugins from the manager.
#
#         Args:
#             ids (list[str]): The ids of the Plugins to remove.
#         """
#         for plugin_id in ids:
#             if plugin_id in self.plugins:
#                 del self.plugins[plugin_id]
#         logger.debug(_('PluginManager purged plugins: {}').format(ids))
#
#
# class Plugin:
#     """The Plugin object models a Synse Plugin that has been registered with
#     Synse Server. It holds the Plugin metadata as well as a reference to a client
#     for communicating with the plugin via the Synse gRPC API.
#
#     On initialization, all Plugin instances are registered with the PluginManager.
#
#     Args:
#         metadata (Metadata): The gRPC Metadata data for the Plugin.
#         address (str): The address of the Plugin.
#         plugin_client (client.PluginClient): The client for communicating with
#             the Plugin.
#     """
#
#     manager = None
#
#     # FIXME: remove address, get it from the client.
#     def __init__(self, metadata, address, plugin_client):
#         self.name = metadata.name
#         self.maintainer = metadata.maintainer
#         self.tag = metadata.tag
#         self.description = metadata.description
#         self.vcs = metadata.vcs
#         self.version = metadata.version
#
#         self.client = plugin_client
#         self.address = address
#         self.protocol = plugin_client.type
#
#         # Register this instance with the manager.
#         self.manager.add(self)
#
#     def __str__(self):
#         return '<Plugin ({}): {}@{}>'.format(self.tag, self.protocol, self.address)
#
#     def id(self):
#         """Get the ID of the plugin. The ID is a composite of the
#         plugin's tag, mode, and address.
#
#         Returns:
#             string: The ID for the Plugin.
#         """
#         return '{}+{}@{}'.format(self.tag, self.protocol, self.address)
#
#
# # Create an instance of the PluginManager to use for all plugins
# Plugin.manager = PluginManager()
#
#
# def get_plugin(name):
#     """Get the Plugin instance with the given name.
#
#     Args:
#         name (str): The name of the plugin.
#
#     Returns:
#         Plugin: The Plugin instance associated with the given name.
#         None: The given name is not associated with a known plugin.
#     """
#     return Plugin.manager.get(name)
#
#
# async def get_plugins():
#     """Get all of the plugins registered with the manager.
#
#     Yields:
#         tuple: A tuple of plugin name and associated Plugin.
#     """
#     for k, v in Plugin.manager.plugins.items():
#         yield k, v
#
#
# def register_plugins():
#     """Register all of the configured plugins.
#
#     Plugins can either use a unix socket or TCP for communication. Unix
#     socket based plugins will be detected from the presence of the socket
#     file in a well-known directory, or via configuration. TCP based plugins
#     will need to be made known to Synse Server via configuration.
#
#     Upon initialization, the Plugin instances are automatically registered
#     with the PluginManager.
#     """
#     # Register plugins from local config (file, env)
#     unix = register_unix()
#     tcp = register_tcp()
#
#     # Get addresses of plugins to register via service discovery
#     discovered = []
#     addresses = kubernetes.discover()
#     for address in addresses:
#         plugin_id = register_plugin(address, 'tcp')
#         if plugin_id is None:
#             logger.error(_('Failed to register plugin with address: {}').format(address))
#             continue
#         discovered.append(plugin_id)
#
#     diff = set(Plugin.manager.plugins) - set(unix + tcp + discovered)
#
#     # Now that we have found all current plugins, we will want to clear out
#     # any old plugins which may no longer be present.
#     logger.debug(_('Plugins to purge from manager: {}').format(diff))
#     Plugin.manager.purge(diff)
#
#     logger.debug(_('Plugin registration complete'))
#
#
# def register_plugin(address, protocol):
#     """Register a plugin. If a plugin with the given address already exists,
#     it will not be re-registered, but its ID will still be returned.
#
#     If a plugin fails to register, None is returned.
#
#     Args:
#         address (str): The address of the plugin to register.
#         protocol (str): The protocol that the plugin uses. This should
#             be one of 'unix', 'tcp'.
#
#     Returns:
#         str: The ID of the plugin that was registered.
#         None: The given address failed to resolve, so no plugin
#             was registered.
#
#     Raises:
#         ValueError: An invalid protocol is specified. The protocol must
#             be one of: 'unix', 'tcp'
#
#     """
#     plugin = Plugin.manager.get_by_address(address)
#     if plugin:
#         logger.debug(_('{} is already registered').format(plugin))
#         return plugin.id()
#
#     # The client does not exist, so we must register it. This means we need to
#     # connect with it to (a) make sure its reachable, and (b) get its metadata
#     # in order to properly create a new Plugin model for it.
#     plugin_client = client.PluginClientV3(address, protocol)
#
#     try:
#         status = plugin_client.test()
#         if not status.ok:
#             logger.warning(_('gRPC Test response was not OK: {}').format(address))
#             return None
#     except Exception as e:
#         logger.warning(_('Failed to reach plugin at address {}: {}').format(address, e))
#         return None
#
#     # If we made it here, we were successful in establishing communication
#     # with the plugin. Now, we should get its metainfo and create a Plugin
#     # instance with it.
#     try:
#         meta = plugin_client.metadata()
#     except Exception as e:
#         logger.warning(_('Failed to get plugin metadata at address {}: {}').format(address, e))
#         return None
#
#     plugin = Plugin(
#         metadata=meta,
#         address=address,
#         plugin_client=plugin_client
#     )
#
#     logger.debug(_('Registered new plugin: {}').format(plugin))
#     return plugin.id()
#
#
# def register_tcp():
#     """Register the plugins that use TCP for communication.
#
#     Return:
#         list[str]: The ids of all plugins that were registered.
#     """
#     registered = []
#
#     configured = config.options.get('plugin.tcp', [])
#     if not configured:
#         logger.info(_('No plugin configurations for TCP'))
#         return registered
#
#     logger.debug(_('TCP plugin configuration: {}').format(configured))
#     for address in configured:
#         plugin_id = register_plugin(address, 'tcp')
#         if plugin_id is None:
#             logger.error(_('Failed to register plugin with address: {}').format(address))
#             continue
#         registered.append(plugin_id)
#
#     logger.info('Registered tcp plugins: {}'.format(registered))
#     return registered
#
#
# def register_unix():
#     """Register the plugins that use a unix socket for communication.
#
#     Unix plugins can be configured in a variety of ways:
#       1.) Listed in the configuration file under plugin.unix
#       2.) Via environment variable
#       2.) Automatically, by placing the socket in the default socket directory
#
#     Here, we will parse the configurations and the default socket directory,
#     add them to the PluginManager, and return a unified list of all known
#     unix-configured plugins.
#
#     Returns:
#         list[str]: The ids of all plugins that were registered.
#     """
#     registered = []
#
#     configured = config.options.get('plugin.unix', [])
#     if not configured:
#         logger.info(_('No plugin configurations for unix'))
#
#     logger.debug(_('unix plugin configuration: {}').format(configured))
#     for address in configured:
#         # The config here should be the path the the unix socket, which is our address.
#         # First, check that the socket exists and that the address is a socket file.
#         if not os.path.exists(address):
#             logger.error(_('Socket {} not found').format(address))
#             continue
#
#         if not stat.S_ISSOCK(os.stat(address).st_mode):
#             logger.error(_('{} is not a socket').format(address))
#             continue
#
#         plugin_id = register_plugin(address, 'unix')
#         if plugin_id is None:
#             logger.error(_('Failed to register plugin with address: {}').format(address))
#             continue
#         registered.append(plugin_id)
#
#     # Now, go through the default socket directory and pick up any sockets that
#     # may be set for automatic registration.
#     if not os.path.exists(const.SOCKET_DIR):
#         logger.debug(
#             _('No default socket path found, no plugins will be registered from {}')
#             .format(const.SOCKET_DIR)
#         )
#     else:
#         logger.debug(
#             _('Registering plugins from default socket directory ({})')
#             .format(const.SOCKET_DIR)
#         )
#
#         for item in os.listdir(const.SOCKET_DIR):
#             logger.debug('  {}'.format(item))
#             address = os.path.join(const.SOCKET_DIR, item)
#
#             # Check if the file is a socket
#             if not stat.S_ISSOCK(os.stat(address).st_mode):
#                 logger.debug(_('{} is not a socket - skipping').format(address))
#                 continue
#
#             plugin_id = register_plugin(address, 'unix')
#             if plugin_id is None:
#                 logger.error(_('Failed to register plugin with address: {}').format(address))
#                 continue
#             registered.append(plugin_id)
#
#             # We want the plugins registered from this default directory to
#             # be surfaced in the config, so we will add it there.
#             if config.options.get('plugin.unix') is None:
#                 config.options.set('plugin.unix', [address])
#             else:
#                 config.options.get('plugin.unix').append(address)
#
#     logger.info('Registered unix plugins: {}'.format(registered))
#     return registered
