"""Synse Server caches and cache utilities."""

import asyncio

import aiocache
import grpc
import synse_grpc.utils

from synse_server import config, plugin
from synse_server.i18n import _
from synse_server.log import logger

transaction_cache = aiocache.SimpleMemoryCache(
    ttl=config.options.get('cache.transaction.ttl', None)
)

device_cache = aiocache.SimpleMemoryCache(
    ttl=config.options.get('cache.device.ttl', None)
)

device_cache_lock = asyncio.Lock()


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
    return list(transaction_cache._cache.keys())


async def add_transaction(transaction_id, device, plugin_name):
    """Add a new transaction to the transaction cache.

    This cache tracks transactions and maps them to the plugin from which they
    originated, as well as the context of the transaction.

    Args:
        transaction_id (str): The ID of the transaction.
        device (str): The ID of the device associated with the transaction.
        plugin_name (str): The name of the plugin to associate with the
            transaction.

    Returns:
        bool: True if successful; False otherwise.
    """
    logger.debug(
        _('caching transaction'), plugin=plugin_name, id=transaction_id, device=device,
    )

    return await transaction_cache.set(
        transaction_id,
        {
            'plugin': plugin_name,
            'device': device,
        },
    )


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
        plugin.manager.update()

    async with device_cache_lock:
        await device_cache.clear()

        for p in plugin.manager:
            logger.debug(_('getting devices from plugin'), plugin=p.tag, plugin_id=p.id)
            try:
                for device in p.client.devices():
                    for tag in device.tags:
                        key = synse_grpc.utils.tag_string(tag)
                        val = await device_cache.get(key)
                        logger.debug('tags key val', key=key, val=val)
                        if val is None:
                            await device_cache.set(key, [device])
                        else:
                            await device_cache.set(key, val + [device])

            except grpc.RpcError as e:
                logger.warning(_('failed to get device(s)'), plugin=p.tag, plugin_id=p.id, error=e)


async def get_device(device_id):
    """Get a device from the device cache by device ID.

    Args:
        device_id (str):
    """
    # Every device has a system-generated ID tag in the format 'system/id:<device id>'
    # which we can use here to get the device. If the ID tag is not in the cache,
    # we take that to mean that there is no such device.
    async with device_cache_lock:
        return await device_cache.get(f'system/id:{device_id}')


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
    results = set()

    # If no tags are provided, there are no filter constraints, so return all
    # cached devices.
    if not tags:
        values = device_cache._cache.values()
        for value in values:
            results.update(set(value))
        return list(results)

    for i, tag in enumerate(tags):
        async with device_cache_lock:
            devices = await device_cache.get(tag)

        # If there are no devices matching the first tag, we will ultimately
        # get nothing, as an intersection with nothing is nothing.
        if devices is None:
            return []

        # For the first tag, populate the results set. Everything after the
        # first tag should be a set intersection.
        if i == 0:
            results = set(devices)
        else:
            results = results.intersection(set(devices))

    return list(results)


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


# import aiocache
# import grpc
#
# import synse_grpc.utils
#
# from synse_server import config, errors, utils
# from synse_server.i18n import _
# from synse_server.log import logger
# from synse_server.plugin import Plugin, get_plugins, register_plugins
#
# # The aiocache configuration
# AIOCACHE = {
#     'default': {
#         'cache': 'aiocache.SimpleMemoryCache',
#         'serializer': {
#             'class': 'aiocache.serializers.NullSerializer'
#         }
#     }
# }
#
# # Synse Server cache namespaces
# NS_TRANSACTION = 'transaction'
# NS_DEVICE_INFO = 'devices'
# NS_PLUGINS = 'plugins'
# NS_SCAN = 'scan'
# NS_INFO = 'info'
# NS_CAPABILITIES = 'capabilities'
#
# # Internal keys into the caches for the data (e.g. dictionaries)
# # being cached.
# DEVICE_INFO_CACHE_KEY = 'meta_cache_key'
# PLUGINS_CACHE_KEY = 'plugins_cache_key'
# SCAN_CACHE_KEY = 'scan_cache_key'
# INFO_CACHE_KEY = 'info_cache_key'
# CAPABILITIES_CACHE_KEY = 'capabilities_cache_key'
#
# # Create caches
# transaction_cache = aiocache.SimpleMemoryCache(namespace=NS_TRANSACTION)
# _device_info_cache = aiocache.SimpleMemoryCache(namespace=NS_DEVICE_INFO)
# _plugins_cache = aiocache.SimpleMemoryCache(namespace=NS_PLUGINS)
# _scan_cache = aiocache.SimpleMemoryCache(namespace=NS_SCAN)
# _info_cache = aiocache.SimpleMemoryCache(namespace=NS_INFO)
# _capabilities_cache = aiocache.SimpleMemoryCache(namespace=NS_CAPABILITIES)
#
# # Configure the caches when the module is loaded.
# # TODO (etd): This used to be a function that was just called in the factory.
# #  need tests to ensure this works and that we aren't configuring the cache
# #  multiple times.
# aiocache.caches.set_config(AIOCACHE)
#
#
# async def clear_cache(namespace):
#     """Clear the cache with the given namespace.
#
#     Cache namespaces are defined in the cache module as variables with
#     a "NS_" prefix.
#
#     Args:
#         namespace (str): The namespace of the cache to clear.
#     """
#     logger.debug(_('Invalidating cache: {}').format(namespace))
#     _cache = aiocache.caches.get('default')
#     return await _cache.clear(namespace=namespace)
#
#
# async def clear_all_meta_caches():
#     """Clear all caches which contain or are derived from meta-information
#     collected from gRPC Metainfo requests.
#     """
#     for ns in [NS_DEVICE_INFO, NS_PLUGINS, NS_INFO, NS_SCAN]:
#         await clear_cache(ns)
#
#
# async def get_transaction(transaction_id):
#     """Get the cached information relating to the given transaction.
#
#     The cached info should include the name of the plugin from which the given
#     transaction originated, and the context of the transaction.
#
#     Args:
#         transaction_id (str): The ID of the transaction.
#
#     Returns:
#         dict: The information associated with a transaction.
#     """
#     return await transaction_cache.get(transaction_id)
#
#
# async def add_transaction(transaction_id, context, plugin_name):
#     """Add a new transaction to the transaction cache.
#
#     This cache tracks transactions and maps them to the plugin from which they
#     originated, as well as the context of the transaction.
#
#     Args:
#         transaction_id (str): The ID of the transaction.
#         context (dict): The action/raw data of the write transaction that
#             can be used to help identify the transaction.
#         plugin_name (str): The name of the plugin to associate with the
#             transaction.
#
#     Returns:
#         bool: True if successful; False otherwise.
#     """
#     ttl = config.options.get('cache.transaction.ttl', None)
#     logger.debug(
#         _('Caching transaction {} from plugin {} ({})').format(
#             transaction_id, plugin_name, context)
#     )
#     return await transaction_cache.set(
#         transaction_id,
#         {
#             'plugin': plugin_name,
#             'context': context
#         },
#         ttl=ttl
#     )
#
#
# async def get_device_info(rack, board, device):
#     """Get the device information for a device.
#
#     Args:
#         rack (str): The rack which the device resides on.
#         board (str): The board which the device resides on.
#         device (str): The ID of the device to get meta-info for.
#
#     Returns:
#         tuple(str, Device): A tuple where the first item is
#             the name of the plugin that the device is associated with and
#             the second item is the device information for that device.
#
#     Raises:
#         errors.DeviceNotFoundError: The given rack-board-device combination
#             does not correspond to a known device.
#     """
#     cid = utils.composite(rack, board, device)
#
#     # This also builds the plugins cache
#     _cache = await get_device_info_cache()
#     dev = _cache.get(cid)
#
#     if dev is None:
#         raise errors.NotFound(
#             _('{} does not correspond with a known device').format(
#                 '/'.join([rack, board, device]))
#         )
#
#     # If the device exists, it will have come from a plugin, so we should
#     # always have the plugin name here.
#     pcache = await _plugins_cache.get(PLUGINS_CACHE_KEY)
#     return pcache.get(cid), dev
#
#
# async def get_capabilities_cache():
#     """Get the cached device capability information for all registered
#     plugins, aggregated from the gRPC Capabilities request.
#
#     If the cache does not exist or has surpassed its TTL, it will be
#     rebuilt.
#
#     Returns:
#         list: A list enumerating each plugin's device kinds and their
#             corresponding capabilities.
#     """
#     # Get the cache and return it if it exists, otherwise, rebuild.
#     value = await _capabilities_cache.get(CAPABILITIES_CACHE_KEY)
#     if value is not None:
#         return value
#
#     capabilities = await _build_capabilities_cache()
#
#     # If the capabilities data is empty when built, we don't want to cache
#     # the empty list, so we will set it to None. Future calls to this function
#     # will then attempt to rebuild the cache.
#     value = capabilities or None
#
#     # Get the cache ttl
#     ttl = config.options.get('cache.meta.ttl', None)
#     await _capabilities_cache.set(CAPABILITIES_CACHE_KEY, value, ttl=ttl)
#
#     return capabilities
#
#
# async def get_device_info_cache():
#     """Get the cached device information aggregated from the gRPC Devices
#     request across all plugins.
#
#     If the cache does not exist or has surpassed its TTL, it will be
#     rebuilt.
#
#     If there are no registered plugins, it attempts to (re-)register them.
#
#     The device info cache is a map where the key is the device id composite
#     and the value is the Device information provided for that device.
#     For example:
#         {
#           "rack1-vec-1249ab12f2ed" : <Device>
#         }
#
#     For the fields of the Device, see the gRPC proto spec:
#     https://github.com/vapor-ware/synse-server-grpc/blob/master/synse.proto
#
#     Returns:
#         dict: The device info dictionary in which the key is the device id
#             and the value is the data associated with that device.
#     """
#     # Get the cache and return it if it exists, otherwise, rebuild.
#     value = await _device_info_cache.get(DEVICE_INFO_CACHE_KEY)
#     if value is not None:
#         return value
#
#     devices, plugins = await _build_device_info_cache()
#
#     # If the device data is empty when built, we don't want to cache an
#     # empty dictionary, so we will set it to None. Future calls to this
#     # function will then attempt to rebuild the cache.
#     devices_value = devices or None
#     plugins_value = plugins or None
#
#     # Get device cache's ttl and update the cache. Use the same ttl for the plugins.
#     # FIXME (etd) - may want to rename the config option
#     ttl = config.options.get('cache.meta.ttl', None)
#     await _device_info_cache.set(DEVICE_INFO_CACHE_KEY, devices_value, ttl=ttl)
#     await _plugins_cache.set(PLUGINS_CACHE_KEY, plugins_value, ttl=ttl)
#
#     return devices
#
#
# async def get_scan_cache():
#     """Get the cached scan results.
#
#     If the scan result cache does not exist or the TTL has expired, the cache
#     will be rebuilt.
#
#     An example of the scan cache structure:
#         {
#           'racks': [
#             {
#               'id': 'rack-1',
#               'boards': [
#                 {
#                   'id': 'vec',
#                   'devices': [
#                     {
#                       'id': '1e93da83dd383757474f539314446c3d',
#                       'info': 'Rack Temperature Spare',
#                       'type': 'temperature'
#                     },
#                     {
#                       'id': '18185208cbc0e5a4700badd6e39bb12d',
#                       'info': 'Rack Temperature Middle Rear',
#                       'type': 'temperature'
#                     }
#                   ]
#                 }
#               ]
#             }
#           ]
#         }
#
#     Returns:
#         dict: A dictionary containing the scan command result.
#     """
#     value = await _scan_cache.get(SCAN_CACHE_KEY)
#     if value is not None:
#         return value
#
#     # If the cache is not found, we will (re)build it from device info cache.
#     _device_info = await get_device_info_cache()
#     scan_cache = _build_scan_cache(_device_info)
#
#     # If the scan data is empty when built, we don't want to cache an empty
#     # dictionary, so we will set it to None. Future calls to get_scan_cache
#     # will then attempt to rebuild the cache.
#     value = scan_cache or None
#
#     # Get the scan cache's ttl and update the cache. This should be the same
#     # ttl that is used by the metainfo cache.
#     ttl = config.options.get('cache.meta.ttl', None)
#     await _scan_cache.set(SCAN_CACHE_KEY, value, ttl=ttl)
#
#     return scan_cache
#
#
# async def get_resource_info_cache():
#     """Get the cached resource info.
#
#     If the resource info cache does not exist or the TTL has expired, the
#     cache will be rebuilt.
#
#     An example of the info cache structure:
#         {
#           'rack-1': {
#             'rack': 'rack-1',
#             'boards': {
#               'vec': {
#                 'board': 'vec',
#                 'devices': {
#                   '1e93da83dd383757474f539314446c3d': {
#                     'timestamp': '2017-11-16 09:16:16.578927204 -0500 EST m=+36.995086134',
#                     'uid': '1e93da83dd383757474f539314446c3d',
#                     'type': 'temperature',
#                     'model': 'MAX11610',
#                     'manufacturer': 'Maxim Integrated',
#                     'protocol': 'i2c',
#                     'info': 'Rack Temperature Spare',
#                     'comment': '',
#                     'location': {
#                       'rack': 'rack-1',
#                       'board': 'vec'
#                     },
#                     'output': [
#                       {
#                         'type': 'temperature',
#                         'data_type': 'float',
#                         'precision': 2,
#                         'unit': {
#                           'name': 'degrees celsius',
#                           'symbol': 'C'
#                         },
#                         'range': {
#                           'min': 0,
#                           'max': 100
#                         }
#                       }
#                     ]
#                   }
#                 }
#               }
#             }
#           }
#         }
#
#     Returns:
#         dict: A dictionary containing the info command result.
#     """
#     value = await _info_cache.get(INFO_CACHE_KEY)
#     if value is not None:
#         return value
#
#     # If the cache is not found, we will (re)build it from device info cache.
#     _device_info = await get_device_info_cache()
#     info_cache = _build_resource_info_cache(_device_info)
#
#     # If the info data is empty when built, we don't want to cache an empty
#     # dictionary, so we will set it to None. Future calls to get_info_cache
#     # will then attempt to rebuild the cache.
#     value = info_cache or None
#
#     # Get the info cache's ttl and update the cache. This should be the same
#     # ttl that is used by the metainfo cache.
#     ttl = config.options.get('cache.meta.ttl', None)
#     await _info_cache.set(INFO_CACHE_KEY, value, ttl=ttl)
#
#     return info_cache
#
#
# async def _build_capabilities_cache():
#     """Construct the list that will become the device capabilities cache.
#
#     Returns:
#         list: A list of dictionaries, where each dictionary corresponds to
#             a registered plugin. The plugin dict will identify the plugin
#             and enumerate the device kinds it supports and the output types
#             supported by those device kinds.
#
#     Raises:
#         errors.InternalApiError: All plugins failed the capabilities request.
#     """
#     logger.debug(_('Building the device capabilities cache'))
#     capabilities = []
#
#     # First, we want to iterate through all of the known plugins and use
#     # their clients to get the capability info for each plugin.
#     plugin_count = len(Plugin.manager.plugins)
#     if plugin_count == 0:
#         logger.debug(_('Manager has no plugins - registering plugins'))
#         register_plugins()
#         plugin_count = len(Plugin.manager.plugins)
#
#     logger.debug(_('Plugins to get capabilities for: {}').format(plugin_count))
#
#     # Track which plugins failed to provide capability info for any reason.
#     failures = {}
#
#     async for plugin_id, plugin in get_plugins():
#         logger.debug('{} - {}'.format(plugin_id, plugin))
#
#         devices = []
#
#         try:
#             for capability in plugin.client.capabilities():
#                 devices.append({
#                     'kind': capability.kind,
#                     'outputs': capability.outputs
#                 })
#
#         except grpc.RpcError as ex:
#             failures[plugin_id] = ex
#             logger.warning(_('Failed to get capability for plugin: {}').format(plugin_id))
#             logger.warning(ex)
#             continue
#
#         capabilities.append({
#             'plugin': plugin.tag,
#             'devices': devices
#         })
#
#     # If we fail to read from all plugins (assuming there were any), then we
#     # can raise an error since it is likely something is mis-configured.
#     if plugin_count != 0 and plugin_count == len(failures):
#         raise errors.ServerError(
#             _('Failed to get capabilities for all plugins: {}').format(failures)
#         )
#
#     return capabilities
#
#
# async def _build_device_info_cache():
#     """Construct the dictionary that will become the device info cache.
#
#     Returns:
#         tuple(dict, dict): A tuple where the first dictionary is the device info
#             dictionary (in which the key is the device id and the value is the
#             data associated with that device), and the second dictionary is the
#             plugins dictionary (in which the device ID is mapped to the name of
#             the plugin which manages it).
#
#     Raises:
#         errors.InternalApiError: All plugins failed the device scan.
#     """
#     logger.debug(_('Building the device cache'))
#     devices, plugins = {}, {}
#
#     # First, we want to iterate through all of the known plugins and
#     # use the associated client to get the device information provided by
#     # that backend.
#     plugin_count = len(Plugin.manager.plugins)
#     if plugin_count == 0:
#         logger.debug(_('Manager has no plugins - registering plugins'))
#         register_plugins()
#         plugin_count = len(Plugin.manager.plugins)
#
#     logger.debug(_('Plugins to scan: {}').format(plugin_count))
#
#     # Track which plugins failed to provide devices for any reason.
#     failures = {}
#
#     async for plugin_id, plugin in get_plugins():
#         logger.debug('{} -- {}'.format(plugin_id, plugin))
#
#         try:
#             for device in plugin.client.devices():
#                 _id = utils.composite(device.location.rack, device.location.board, device.uid)
#                 devices[_id] = device
#                 plugins[_id] = plugin_id
#
#         # We do not want to fail the scan if a single plugin fails to provide
#         # device information.
#         #
#         # FIXME (etd): instead of just logging out the errors, we could either:
#         #   - update the response scheme to hold an 'errors' field which will alert
#         #     the user of these partial non-fatal errors.
#         #   - update the API to add a url to check the currently configured plugins
#         #     and their 'health'/'state'.
#         #   - both
#         except grpc.RpcError as ex:
#             failures[plugin_id] = ex
#             logger.warning(_('Failed to get device info for plugin: {}').format(plugin_id))
#             logger.warning(ex)
#
#     # If we fail to read from all plugins (assuming there were any), then we
#     # can raise an error since it is likely something is mis-configured.
#     if plugin_count != 0 and plugin_count == len(failures):
#         raise errors.ServerError(
#             _('Failed to scan all plugins: {}').format(failures)
#         )
#
#     return devices, plugins
#
#
# def _build_scan_cache(device_info):
#     """Build the scan cache.
#
#     This builds the scan cache, adhering to the Scan response scheme,
#     using the contents of the device-info cache.
#
#     Args:
#         device_info (dict): The device info cache dictionary.
#
#     Returns:
#         dict: The constructed scan cache.
#     """
#     logger.debug(_('Building the scan cache'))
#     scan_cache = {}
#
#     # The _tracked dictionary is used to help track which racks and
#     # boards already exist while we are building the cache. It should
#     # look something like:
#     #
#     #   _tracked = {
#     #       'rack_id_1': {
#     #           'rack': <>,
#     #           'boards': {
#     #               'board_id_1': <>,
#     #               'board_id_2': <>
#     #           }
#     #       }
#     #   }
#     #
#     # Where we track racks by their id, map each rack to a dictionary
#     # containing the rack info, and track each board on the rack under
#     # the 'boards' key.
#     _tracked = {}
#
#     for source in device_info.values():
#         rack_id = source.location.rack
#         board_id = source.location.board
#         device_id = source.uid
#         plugin = source.plugin
#         sort_ordinal = source.sortOrdinal
#
#         # The given rack does not yet exist in our scan cache.
#         # In this case, we will create it, along with the board
#         # and device that the source record provides.
#         if rack_id not in _tracked:
#             new_board = {
#                 'id': board_id,
#                 'devices': [
#                     {
#                         'id': device_id,
#                         'info': source.info,
#                         'type': utils.type_from_kind(source.kind),
#                         'plugin': plugin,
#                         'sort_ordinal': sort_ordinal,
#                     }
#                 ]
#             }
#
#             new_rack = {
#                 'id': rack_id,
#                 'boards': []
#             }
#
#             # Update the _tracked dictionary with references to the
#             # newly created rack and board.
#             _tracked[rack_id] = {
#                 'rack': new_rack,
#                 'boards': {
#                     board_id: new_board
#                 }
#             }
#
#         # The rack does exist in the scan cache. In this case, we will
#         # check if the board exists. If not, we will create it with the
#         # device that the source record provides. If so, we will append
#         # the device information provided by the source record to the
#         # existing board.
#         else:
#             r = _tracked[rack_id]
#             if board_id not in r['boards']:
#                 new_board = {
#                     'id': board_id,
#                     'devices': [
#                         {
#                             'id': device_id,
#                             'info': source.info,
#                             'type': utils.type_from_kind(source.kind),
#                             'plugin': plugin,
#                             'sort_ordinal': sort_ordinal,
#                         }
#                     ]
#                 }
#
#                 r['boards'][board_id] = new_board
#
#             else:
#                 r['boards'][board_id]['devices'].append({
#                     'id': device_id,
#                     'info': source.info,
#                     'type': utils.type_from_kind(source.kind),
#                     'plugin': plugin,
#                     'sort_ordinal': sort_ordinal,
#                 })
#
#     if _tracked:
#         # Add the root 'racks' field to the scan data
#         scan_cache['racks'] = []
#
#         # Sort the racks in the _tracked dictionary by rack id
#         sorted_rack_ids = sorted(_tracked.keys())
#         for rid in sorted_rack_ids:
#             rack_ref = _tracked[rid]
#             rack = rack_ref['rack']
#
#             # Sort each board on each rack by board id
#             sorted_board_ids = sorted(rack_ref['boards'].keys())
#             for bid in sorted_board_ids:
#                 board = rack_ref['boards'][bid]
#
#                 # Sort all devices on each board by plugin and sort ordinal
#                 board['devices'] = sorted(
#                     board['devices'],
#                     key=lambda d: (d['plugin'], d['sort_ordinal'], d['id'])
#                 )
#
#                 # Delete the plugin and sort_ordinal from the scan result after sorting.
#                 for device in board['devices']:
#                     del device['plugin']
#                     del device['sort_ordinal']
#
#                 rack['boards'].append(board)
#             scan_cache['racks'].append(rack)
#     return scan_cache
#
#
# def _build_resource_info_cache(metainfo):
#     """Build the resource info cache.
#
#     This builds the info cache, adhering to the Info response scheme,
#     using the contents of the meta-info cache.
#
#     Args:
#         metainfo (dict): The meta-info cache dictionary.
#
#     Returns:
#         dict: The constructed info cache.
#     """
#     logger.debug(_('Building the info cache'))
#     info_cache = {}
#
#     for source in metainfo.values():
#
#         src = synse_grpc.utils.to_dict(source)
#
#         rack = source.location.rack
#         board = source.location.board
#         device = source.uid
#
#         if rack in info_cache:
#             rdata = info_cache[rack]
#             if board in rdata['boards']:
#                 bdata = rdata['boards'][board]
#                 if device not in bdata['devices']:
#                     bdata['devices'][device] = src
#             else:
#                 rdata['boards'][board] = {
#                     'board': board,
#                     'devices': {device: src}
#                 }
#         else:
#             info_cache[rack] = {
#                 'rack': rack,
#                 'boards': {
#                     board: {
#                         'board': board,
#                         'devices': {device: src}
#                     }
#                 }
#             }
#
#     return info_cache
