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

    def has_plugins(self):
        """Convenience function to determine whether any plugins are
        currently registered with the manager.

        Returns:
            bool: True if any number of plugins are registered with the
            manager; False otherwise.
        """
        return len(self.plugins) > 0

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

        plugin.mark_active()
        return plugin.id

    def load(self):
        """Load plugins from configuration.

        This should be called on Synse Server initialization.

        Raises:
            errors.ServerError: Configured plugin already exists.
        """
        logger.info(_('loading plugins from configuration'))

        # Get plugin configs for TCP-configured plugins
        cfg_tcp = config.options.get('plugin.tcp', [])
        for address in cfg_tcp:
            logger.debug(_('plugin from config'), mode='tcp', address=address)
            self.register(address=address, protocol='tcp')

        # Get plugin configs for Unix socket-configured plugins
        cfg_unix = config.options.get('plugin.unix', [])
        for address in cfg_unix:
            logger.debug(_('plugin from config'), mode='unix', address=address)
            self.register(address=address, protocol='unix')

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

    def refresh(self):
        """Refresh the manager's tracked plugin state.

        This refreshes plugin state by checking if any new plugins are available
        to Synse Server and updating the active state for each plugin.

        Refresh does not re-load plugins from configuration. That is done on
        initialization. New plugins may only be added at runtime via plugin
        discovery mechanisms.
        """

        logger.debug(_('refreshing plugin manager'))

        for address, protocol in self.discover():
            for plugin in self.plugins.values():
                if plugin.address == address and plugin.protocol == protocol:
                    logger.debug(
                        _('discovered plugin already registered'),
                        address=address, protocol=protocol,
                    )
                    break
            else:
                try:
                    self.register(address=address, protocol=protocol)
                except Exception as e:
                    # Do not raise. If we fail to register, it is either because the
                    # plugin already exists or because we could not communicate with
                    # it. Future refreshes will attempt to re-register in this case.
                    # Log the failure and continue trying to register any remaining
                    # discovered plugins.
                    logger.warning(
                        _('failed to register plugin'), address=address, protocol=protocol, error=e
                    )

        logger.debug(_('plugin manager refresh complete'), plugin_count=len(self.plugins))


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
        self.active = False
        self.client = client

        self.address = self.client.get_address()
        self.protocol = self.client.protocol

        self.metadata = info
        self.version = version

        self.tag = info.get('tag')
        if self.tag is None:
            raise ValueError('plugin: required field "tag" missing')

        self.id = info.get('id')
        if self.id is None:
            raise ValueError('plugin: required field "id" missing')

    def __str__(self):
        return f'<Plugin ({self.tag}): {self.id}>'

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Upon exiting the plugin context, check for any raised exception. If no
        # exception was found, mark the plugin as active. Otherwise, mark it as
        # inactive.
        if exc_type is None or isinstance(exc_val, client.errors.PluginError):
            self.mark_active()
        else:
            self.mark_inactive()

    def mark_active(self):
        """Mark the plugin as active, if it is not already active."""

        if not self.active:
            logger.info(_('marking plugin as active'), id=self.id, tag=self.tag)
            self.active = True

    def mark_inactive(self):
        """Mark the plugin as inactive, if it is not already inactive."""

        if self.active:
            logger.info(_('marking plugin as inactive'), id=self.id, tag=self.tag)
            self.active = False
