"""Synse Server caches and cache utilities."""

import asyncio

import aiocache
import grpc
import synse_grpc.utils

from synse_server import config, plugin
from synse_server.i18n import _
from synse_server.log import logger

# The in-memory cache implementation stores data in a class member variable,
# so all instance of the in memory cache will reference that data structure.
# In order to separate transactions from devices, we need each cache to define
# its own namespace.
NS_TRANSACTION = 'synse.txn.'
NS_DEVICE = 'synse.dev.'
NS_ALIAS = 'synse.alias.'

transaction_cache = aiocache.SimpleMemoryCache(
    ttl=config.options.get('cache.transaction.ttl', None),
    namespace=NS_TRANSACTION,
)

device_cache = aiocache.SimpleMemoryCache(
    namespace=NS_DEVICE,
)

alias_cache = aiocache.SimpleMemoryCache(
    namespace=NS_ALIAS,
)

device_cache_lock = asyncio.Lock()
alias_cache_lock = asyncio.Lock()


async def get_transaction(transaction_id):
    """Get the cached transaction information with the provided ID.

    If the provided transaction ID does not correspond to a known transaction,
    None is returned.

    Args:
        transaction_id (str): The ID of the transaction.

    Returns:
        dict: The information associated with the transaction.
    """
    return await transaction_cache.get(transaction_id)


def get_cached_transaction_ids():
    """Get a list of all the currently cached transaction IDs.

    Note that the list of IDs that this provides is not guaranteed to
    be correct at any point in the future. Items are expired from
    the cache asynchronously, so this only serves as a snapshot at
    a given point in time.

    Returns:
        list[str]: The IDs of all actively tracked transactions.
    """
    return [k[len(NS_TRANSACTION):] for k in transaction_cache._cache.keys()
            if k.startswith(NS_TRANSACTION)]


async def add_transaction(transaction_id, device, plugin_id):
    """Add a new transaction to the transaction cache.

    This cache tracks transactions and maps them to the plugin from which they
    originated, as well as the context of the transaction.

    Args:
        transaction_id (str): The ID of the transaction.
        device (str): The ID of the device associated with the transaction.
        plugin_id (str): The ID of the plugin to associate with the
            transaction.

    Returns:
        bool: True if successful; False otherwise.
    """
    logger.debug(
        _('caching transaction'), plugin=plugin_id, id=transaction_id, device=device,
    )

    return await transaction_cache.set(
        transaction_id,
        {
            'plugin': plugin_id,
            'device': device,
        },
    )


async def add_alias(alias, device):
    """Add a new device alias to the alias cache.

    Args:
        alias (str): The alias of the device.
        device (V3Device): The device associated with the given alias.

    Returns:
        bool: True if successful; False otherwise.
    """
    logger.debug(
        _('adding alias to cache'), alias=alias, device=device.id,
    )

    async with alias_cache_lock:
        return await alias_cache.set(alias, device)


async def get_alias(alias):
    """Get a device by its alias from the alias cache.

    Args:
        alias (str): The alias of the device to look up.

    Returns:
        V3Device | None: The device with the specified alias. If the
        alias does not match a device, None is returned.
    """

    async with alias_cache_lock:
        return await alias_cache.get(alias)


# FIXME (etd): Should this be changes so we have two separate functions? One
#   "update" function, and one "add_device" function?
async def update_device_cache():
    """Update the device cache.

    The device cache consists of string-ified tags as the keys, and a list
    of Device info dictionaries as the values. This allows the most flexible
    means of searching, as we can search for devices by single tag, multiple
    tags (and get the set intersection), or by ID (using the special ID tag).

    Example:
         "default/foo": [{...}, {...}, {...}]
         "default/x:bar": [{...}]
         "vaporio/svc:xyz": [{...}, {...}]

    TODO: The cache structure here is quite different from how it was in
      Synse v2. We will need to profile/examine performance and behavior
      with this implementation to ensure that it does not negatively impact
      Synse Server.
    """
    logger.debug(_('updating the device cache'))

    # Get the list of all devices (including their associated tags) from
    # each registered plugin. This device data will be used to generate
    # the cache.
    #
    # If there are no plugins currently registered, attempt
    # to re-register. This can be the case when Synse Server is first
    # starting up, being restarted, or is recovering from a networking error.
    if len(plugin.manager.plugins) == 0:
        logger.debug(_('no plugins found when updating device cache'))
        plugin.manager.refresh()

    async with device_cache_lock:
        await device_cache.clear()

        for p in plugin.manager:
            logger.debug(_('getting devices from plugin'), plugin=p.tag, plugin_id=p.id)
            try:
                with p as client:
                    # todo: exception handling
                    for device in client.devices():
                        # Update the alias cache if the device has an alias.
                        if device.alias:
                            await add_alias(device.alias, device)

                        # Update the device cache, mapping each tag to the device.
                        for tag in device.tags:
                            key = synse_grpc.utils.tag_string(tag)
                            val = await device_cache.get(key)
                            if val is None:
                                await device_cache.set(key, [device])
                            else:
                                await device_cache.set(key, val + [device])

            except grpc.RpcError as e:
                logger.warning(_('failed to get device(s)'), plugin=p.tag, plugin_id=p.id, error=e)


async def get_device(device_id):
    """Get a device from the device cache by device ID or alias.

    We can not reasonably tell whether the provided device_id is
    an ID or an alias ahead of time. First, the device ID is looked
    up via its ID tag in the tag cache. If there is no match, an
    alias lookup is performed.

    Args:
        device_id (str): The ID or alias of the device to get.

    Returns:
        V3Device | None: The device with the corresponding ID. If no device
        has the specified ID, None is returned.
    """
    device = None

    # Every device has a system-generated ID tag in the format 'system/id:<device id>'
    # which we can use here to get the device. If the ID tag is not in the cache,
    # we take that to mean that there is no such device.
    async with device_cache_lock:
        result = await device_cache.get(f'system/id:{device_id}')

        # The device cache stores all devices in a list against the key, even
        # if only one device exists for that key. If the results list is not
        # empty, return the first element of the list - there should only be
        # one element; otherwise, return None.
        if result:
            device = result[0]

    # No device was found from an ID lookup. Try looking up the ID in the
    # alias cache.
    if not device:
        device = await get_alias(device_id)

    return device


async def get_devices(*tags):
    """Get the device(s) from the device cache which match the provided tag(s).

    Note that if multiple tags are specified, the result set is subtractive. That
    is to say, only devices matching all of the specified tags are returned (set
    intersection, not set union).

    Args:
        tags (iterable[str]): The tags to filter devices by.

    Returns:
        list[V3Device]: The devices which match the specified tags.
    """
    # Results are a dict since the V3Device object is not hashable. To ensure
    # we don't include duplicate device records in the response, we will add
    # them to the dict keyed off their ID. The resulting dict values should
    # then be unique.
    results = dict()

    # If no tags are provided, there are no filter constraints, so return all
    # cached devices.
    if not tags:
        for key, devices in device_cache._cache.items():
            if not key.startswith(NS_DEVICE):
                continue
            for device in devices:
                # for device in devices:
                results[device.id] = device

        return list(results.values())

    for i, tag in enumerate(tags):
        async with device_cache_lock:
            devices = await device_cache.get(tag)

        # If there are no devices matching the first tag, we will ultimately
        # get nothing, as an intersection with nothing is nothing.
        if devices is None:
            return []

        # For the first tag, populate the results dict. Everything after the
        # first tag should be a set intersection. This means we subtract the
        # set difference from the results dict for all subsequent devices.
        if i == 0:
            for device in devices:
                results[device.id] = device
        else:
            diff = set(results.keys()).difference(set([d.id for d in devices]))
            for item in diff:
                del results[item]

            # If there is nothing left in the results, return.
            if not results:
                return []

    return list(results.values())


def get_cached_device_tags():
    """Get a list of all the currently cached device tags.

    Note that the list of IDs that this provides is not guaranteed to
    be correct at any point in the future. Items are expired from
    the cache asynchronously, so this only serves as a snapshot at
    a given point in time.

    Returns:
        list[str]: The tags of all actively tracked devices.
    """
    return [k[len(NS_DEVICE):] for k in device_cache._cache.keys() if k.startswith(NS_DEVICE)]


async def get_plugin(device_id):
    """Get the Plugin instance associated with the specified device.

    Args:
        device_id (str): The ID of the device to get the associated
            Plugin instance for.

    Returns:
        Plugin | None: The Plugin instance associated with the specified
        device. If the specified device does not exist, this will return
        None.
    """
    device = await get_device(device_id)
    if device is None:
        return None
    return plugin.manager.get(device.plugin)
