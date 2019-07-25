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
        """
        # Prior to registering the plugin, we need to get the plugin metadata
        # and ensure that we can connect to the plugin. These calls may raise
        # an exception - we want to let them propagate up to signal that registration
        # for the particular address failed.
        c = client.PluginClientV3(
            address=address,
            protocol=protocol,
            timeout=config.options.get('grpc.timeout'),
            tls=config.options.get('grpc.tls.cert'),
        )
        meta = c.metadata()
        ver = c.version()

        plugin = Plugin(
            info=utils.to_dict(meta),
            version=utils.to_dict(ver),
            client=c,
        )

        if plugin.id in self.plugins:
            # The plugin has already been registered. There is nothing left to
            # do here, so just log and move on.
            logger.debug(_('plugin with id already registered'), id=plugin.id)
        else:
            self.plugins[plugin.id] = plugin
            logger.debug(_('registered plugin'), id=plugin.id, tag=plugin.tag)

        plugin.mark_active()
        return plugin.id

    @classmethod
    def load(cls):
        """Load plugins from configuration.

        This should be called on Synse Server initialization.

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

        return configs

    @classmethod
    def discover(cls):
        """Discover plugins via the supported discovery methods.

        Currently, plugin discovery is supported by kubernetes service endpoints.

        Returns:
            list[tuple[str, str]]: A list of plugin configuration tuples where the
            first element is the plugin address and the second element is the protocol.
        """
        configs = []

        try:
            addresses = kubernetes.discover()
        except Exception as e:
            logger.info(_('failed plugin discovery via kubernetes'), error=e)
        else:
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

        for address, protocol in self.load():
            try:
                self.register(address=address, protocol=protocol)
            except Exception as e:
                # Do not raise. This could happen if we can't communicate with
                # the configured plugin. Future refreshes will attempt to re-register
                # in this case. Log the failure and continue trying to register
                # any remaining plugins.
                logger.warning(
                    _('failed to register configured plugin'),
                    address=address, protocol=protocol, error=e,
                )
                continue

        for address, protocol in self.discover():
            try:
                self.register(address=address, protocol=protocol)
            except Exception as e:
                # Do not raise. This could happen if we can't communicate with
                # the configured plugin. Future refreshes will attempt to re-register
                # in this case. Log the failure and continue trying to register
                # any remaining plugins.
                logger.warning(
                    _('failed to register discovered plugin'),
                    address=address, protocol=protocol, error=e,
                )
                continue

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
        if not self.tag:
            raise ValueError('plugin: required field "tag" missing')

        self.id = info.get('id')
        if not self.id:
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
            logger.info(
                'marking plugin inactive',
                exc_type=exc_type,
                exc_val=exc_val,
                exc_tb=exc_tb,
                id=self.id,
            )
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
