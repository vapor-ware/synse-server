"""Management and access logic for configured plugin backends."""

import asyncio
import time
from typing import Dict, List, Optional, Tuple, Union

from structlog import get_logger
from synse_grpc import client, utils

from synse_server import backoff, config, loop
from synse_server.discovery import kubernetes
from synse_server.metrics import MetricsInterceptor, Monitor

logger = get_logger()


class PluginManager:
    """A manager for plugins registered with the Synse Server instance.

    The PluginManager state is kept as a class member, so all instances
    of the manager should operate on the same plugin state. The PluginManager
    is also iterable, where iterating over the manager will provide the
    snapshot of currently registered plugins.

    Attributes:
        is_refreshing: A state flag determining whether the manager is
            currently performing a plugin refresh. Since plugin refresh
            may be started via async task or API call, this state variable
            is used to prevent two refreshes from happening simultaneously.
    """

    plugins: Dict[str, 'Plugin'] = {}

    def __init__(self):
        self.is_refreshing = False

    def __iter__(self) -> 'PluginManager':
        self._snapshot = list(self.plugins.values())
        self._idx = 0
        return self

    def __next__(self) -> 'Plugin':
        if self._idx >= len(self._snapshot):
            raise StopIteration

        plugin = self._snapshot[self._idx]
        self._idx += 1
        return plugin

    def has_plugins(self) -> bool:
        """Convenience function to determine whether any plugins are
        currently registered with the manager.

        Returns:
            True if any number of plugins are registered with the
            manager; False otherwise.
        """
        return len(self.plugins) > 0

    def get(self, plugin_id: str) -> Union['Plugin', None]:
        """Get a ``Plugin`` by ID.

        Args:
            plugin_id: The ID of the plugin.

        Returns:
            The plugin with the matching ID. If the given ID is not associated
            with a registered plugin, None is returned.
        """
        return self.plugins.get(plugin_id)

    def register(self, address: str, protocol: str) -> str:
        """Register a new Plugin with the manager.

        With the provided address and communication protocol, the manager
        will attempt to establish communication with the plugin to get its
        metadata. If successful, it will generate a new Plugin instance for
        the plugin and register it in the manager state.

        Args:
            address: The address of the plugin to register.
            protocol: The protocol that the plugin uses. This must be
                one of: 'unix', 'tcp'.

        Returns:
            The ID of the plugin that was registered.
        """
        logger.info('registering new plugin', addr=address, protocol=protocol)

        interceptors = []
        if config.options.get('metrics.enabled'):
            logger.debug('application metrics enabled: registering gRPC interceptor')
            interceptors = [MetricsInterceptor()]

        # Prior to registering the plugin, we need to get the plugin metadata
        # and ensure that we can connect to the plugin. These calls may raise
        # an exception - we want to let them propagate up to signal that registration
        # for the particular address failed.
        c = client.PluginClientV3(
            address=address,
            protocol=protocol,
            timeout=config.options.get('grpc.timeout'),
            tls=config.options.get('grpc.tls.cert'),
            interceptors=interceptors,
        )
        meta = c.metadata()
        ver = c.version()

        plugin = Plugin(
            info=utils.to_dict(meta),
            version=utils.to_dict(ver),
            client=c,
            loop=loop.synse_loop,
        )
        logger.debug(
            'loaded plugin info',
            id=plugin.id, version=plugin.version, addr=plugin.address, tag=plugin.tag,
        )

        if plugin.id in self.plugins:
            # The plugin has already been registered. There is nothing left to
            # do here, so just log and move on.
            logger.debug('plugin with id already registered - skipping', id=plugin.id)
        else:
            self.plugins[plugin.id] = plugin
            logger.info('successfully registered new plugin', id=plugin.id, tag=plugin.tag)

        self.plugins[plugin.id].mark_active()
        return plugin.id

    @classmethod
    def load(cls) -> List[Tuple[str, str]]:
        """Load plugins from configuration.

        This should be called on Synse Server initialization.

        Returns:
            A list of plugin configuration tuples where the first element is the
            plugin address and the second element is the protocol.
        """
        logger.info('loading plugins from configuration')

        configs = []

        # Get plugin configs for TCP-configured plugins
        cfg_tcp = config.options.get('plugin.tcp', [])
        for address in cfg_tcp:
            logger.debug('loading plugin from config', mode='tcp', address=address)
            configs.append((address, 'tcp'))

        # Get plugin configs for Unix socket-configured plugins
        cfg_unix = config.options.get('plugin.unix', [])
        for address in cfg_unix:
            logger.debug('loading plugin from config', mode='unix', address=address)
            configs.append((address, 'unix'))

        return configs

    @classmethod
    def discover(cls) -> List[Tuple[str, str]]:
        """Discover plugins via the supported discovery methods.

        Currently, plugin discovery is supported by kubernetes service endpoints.

        Returns:
            A list of plugin configuration tuples where the first element is the
            plugin address and the second element is the protocol.
        """
        configs = []

        try:
            addresses = kubernetes.discover()
        except Exception as e:
            logger.info('failed plugin discovery via Kubernetes', error=e)
        else:
            for address in addresses:
                configs.append((address, 'tcp'))

        logger.debug('found addresses via plugin discovery', addresses=configs)
        return configs

    def bucket_plugins(
            self,
            new_plugins: List[Tuple[str, str]],
    ) -> Tuple[List['Plugin'], List[Tuple[str, str]], List['Plugin']]:
        """Bucket the registered plugins and potential new plugins based on a
        given config for new plugins.

        The config consists of a collection of tuples, where each tuple is the
        basic config for the plugin. The first element is the plugin address.
        The second element is the protocol (TCP, unix).

        Three buckets are created:
          1. Existing plugins: These are the plugins in the given config which
             have already been registered with the manager.
          2. New plugins: These are the plugins in the given config which are
             unknown to the manager as they have not yet been registered.
          3. Removed plugins: These are the plugins which are currently registered
             with the manager but did not show up in the given config.
        """

        existing, new, removed = [], [], []
        cfgs = []

        for p in self.plugins.values():
            cfg = (p.address, p.protocol)
            cfgs.append(cfg)

            if cfg in new_plugins:
                existing.append(p)
            else:
                removed.append(p)

        for cfg in new_plugins:
            if cfg not in cfgs:
                new.append(cfg)

        return existing, new, removed

    def refresh(self) -> None:
        """Refresh the manager's tracked plugin state.

        This refreshes plugin state by checking if any new plugins are available
        to Synse Server. Once any plugins are added or disabled, it will also
        update the active/inactive state of each of the enabled plugins.

        Refresh does not re-load plugins from configuration. That is done on
        initialization. New plugins may only be added at runtime via plugin
        discovery mechanisms.
        """
        if self.is_refreshing:
            logger.debug('manager is already refreshing')
            return

        try:
            self.is_refreshing = True
            logger.debug('refreshing plugin manager')
            start = time.time()

            plugins = []
            plugins.extend(self.load())
            plugins.extend(self.discover())

            existing, new, removed = self.bucket_plugins(plugins)
            logger.debug('bucketed plugins', existing=existing, new=new, removed=removed)

            # Register all new plugins
            for plugin in new:
                try:
                    self.register(address=plugin[0], protocol=plugin[1])
                except Exception as e:
                    # Do not raise. This could happen if we can't communicate with
                    # the configured plugin. Future refreshes will attempt to re-register
                    # in this case. Log the failure and continue trying to register
                    # any remaining plugins.
                    logger.warning(
                        'failed to register configured plugin - will attempt re-registering later',
                        address=plugin[0], protocol=plugin[1], error=e,
                    )
                    continue

            # Disable all removed plugins and stop any active tasks they may be running.
            for plugin in removed:
                logger.warn(
                    'registered plugin not found during refresh, marking as disabled',
                    plugin=plugin,
                )
                plugin.disabled = True
                plugin.cancel_tasks()

                # Update the exported metrics disabled plugins gauge: add a disabled plugin
                Monitor.plugin_disabled.labels(plugin.id).inc()

            # Check if the existing plugin was disabled. If so, re-enable it. Otherwise, there
            # is nothing to do here.
            for plugin in existing:
                if plugin.disabled:
                    logger.info(
                        'refresh found previously disabled plugin; re-enabling',
                        plugin=plugin,
                    )
                    plugin.disabled = False

                    # Update the exported metrics disabled plugins gauge: remove a disabled plugin
                    Monitor.plugin_disabled.labels(plugin.id).dec()

        finally:
            self.is_refreshing = False

        # Now, ensure that all enabled plugins have their active/inactive state refreshed.
        for p in self.plugins.values():
            p.refresh_state()

        logger.debug(
            'plugin manager refresh complete',
            plugin_count=len(self.plugins),
            elapsed_time=time.time() - start,
        )

    def all_ready(self) -> bool:
        """Check to see if all registered plugins are ready.

        If a single plugin is not ready, this returns False. If no plugins are
        registered, this returns True. In such a case, it is up to the caller to
        perform additional checks for number of registered plugins.
        """
        return all(plugin.is_ready() for plugin in self)


# A module-level instance of the plugin manager. This makes it easier to use
# the manager in various places, without having to initialize a new instance.
manager = PluginManager()


class Plugin:
    """Plugin stores the metadata for a registered plugin along with a client
    for communicating with the plugin via the Synse gRPC API.

    Generally, plugins are looked up by ID as each device will specify which
    plugin owns it via the plugin ID. Plugin IDs are generated by the plugin.

    Args:
        info: A dictionary containing the metadata for the associated plugin.
        version: A dictionary containing the version information for the
            associated plugin .
        client: The Synse v3 gRPC client used to communicate with the plugin.
        loop: The event loop to run plugin tasks on.
    """

    def __init__(
            self,
            info: dict,
            version: dict,
            client: client.PluginClientV3,
            loop: asyncio.AbstractEventLoop = None,
    ) -> None:

        self.loop = loop or asyncio.get_event_loop()
        self.active = False
        self.disabled = False
        self.client = client

        self._disconnects = 0
        self._connects = 0

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

        # Now that we have the identity of the plugin, we can update the gRPC
        # interceptor so it includes this information in its labels.
        if self.client.interceptors:
            for interceptor in self.client.interceptors:
                interceptor.plugin = self.id

        self._reconnect_task: Optional[asyncio.Task] = None

    def __str__(self) -> str:
        return f'<Plugin ({self.tag}): {self.id}>'

    def __repr__(self) -> str:
        return str(self)

    def __del__(self) -> None:
        self.cancel_tasks()

    def __enter__(self) -> client.PluginClientV3:
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # Upon exiting the plugin context, check for any raised exception. If no
        # exception was found, mark the plugin as active. Otherwise, mark it as
        # inactive.
        if exc_type is None or isinstance(exc_val, client.errors.PluginError):
            self.mark_active()
        else:
            logger.info(
                'error on plugin context exit, will attempt reconnect',
                exc_type=exc_type,
                exc_val=exc_val,
                exc_tb=exc_tb,
                id=self.id,
            )
            self._reconnect_task = asyncio.create_task(self._reconnect())
            self.mark_inactive()

    async def _reconnect(self):
        """Reconnect to the plugin instance.

        This method is run as a Task when the plugin is exiting its
        context manager in a failed state due to error. This is indicative
        of a failure to connect with the plugin.
        """
        start = time.time()
        _l = logger.bind(plugin=self.id)
        _l.info('starting plugin reconnect task')
        bo = backoff.ExponentialBackoff()

        while True:
            _l.debug('plugin reconnect task: attempting reconnect')
            try:
                self.client.test()
            except Exception as ex:
                _l.info('plugin reconnect task: failed to reconnect to plugin', error=ex)
                # The plugin should still be in the inactive state, but we re-set
                # it here to ensure it is true.
                self.mark_inactive()
            else:
                self.mark_active()
                _l.info(
                    'plugin reconnect task: established connection with plugin',
                    total_time=time.time() - start,
                )
                return

            delay = bo.delay()
            _l.debug('plugin reconnect task: waiting until next retry', delay=delay)
            await asyncio.sleep(delay)

    def refresh_state(self):
        """Refresh the state of the plugin.

        When a plugin becomes inactive, it will start a task to periodically retry
        establishing a connection to the plugin with exponential backoff. This can be
        good at automated recovery, especially for quick intermittent errors. It
        becomes less useful when there is plugin maintenance or some other longer
        window of downtime, as the exponential backoff will take a while to re-establish
        a connection.

        To alleviate this potential use case, this function performs the same state
        refresh for the plugin, but it is executed manually via a call to the
        `/plugin?refresh=true`. Setting refresh to true for the endpoint will both
        ensure that Synse Server refreshes the state of known plugins, and that it
        also refreshes the state of each existing individual plugin to ensure that
        its active/inactive state is up-to-date.
        """
        _l = logger.bind(plugin=self.id)
        _l.info('refreshing plugin state')

        if self.disabled:
            _l.info('plugin is disabled, will not refresh')
            return

        try:
            self.client.test()
        except Exception as ex:
            _l.debug('plugin refresh: failed to connect to plugin', errror=ex)
            self.mark_inactive()
        else:
            _l.debug('plugin refresh: successfully connected to plugin')
            self.mark_active()

    def is_ready(self):
        """Check whether the plugin is ready to communicate with.

        This check ensures that the plugin is not disabled and that it is in the
        active state.
        """
        return self.active and not self.disabled

    def cancel_tasks(self) -> None:
        """Cancel any tasks associated with the plugin."""
        if self.loop.is_running():
            if self._reconnect_task is not None and (
                not self._reconnect_task.done() or not self._reconnect_task.cancelled()
            ):
                logger.debug('cancelling reconnect task', plugin=self.id)
                self._reconnect_task.cancel()

    def mark_active(self) -> None:
        """Mark the plugin as active, if it is not already active."""

        if not self.active:
            logger.info('marking plugin as active', id=self.id, tag=self.tag)
            self.active = True
            self._connects += 1

            # Update exported metrics
            Monitor.plugin_active.labels(self.id).inc()
            Monitor.plugin_connects.labels(self.id).inc()

    def mark_inactive(self) -> None:
        """Mark the plugin as inactive, if it is not already inactive."""

        if self.active:
            logger.info('marking plugin as inactive', id=self.id, tag=self.tag)
            self.active = False
            self._disconnects += 1

            # Update exported metrics
            Monitor.plugin_active.labels(self.id).dec()
            Monitor.plugin_disconnects.labels(self.id).inc()
