"""Synse Server caches and cache utilities.
"""

import aiocache
import grpc

from synse import config, errors, utils
from synse.i18n import gettext
from synse.log import logger
from synse.plugin import Plugin, register_plugins
from synse.proto import util as putil

# Define namespace for caches
NS_TRANSACTION = 'transaction'
NS_META = 'meta'
NS_SCAN = 'scan'
NS_INFO = 'info'

# Define cached key for caches
META_CACHE_KEY = 'meta_cache_key'
SCAN_CACHE_KEY = 'scan_cache_key'
INFO_CACHE_KEY = 'info_cache_key'

# Create caches
transaction_cache = aiocache.SimpleMemoryCache(namespace=NS_TRANSACTION)
_meta_cache = aiocache.SimpleMemoryCache(namespace=NS_META)
_scan_cache = aiocache.SimpleMemoryCache(namespace=NS_SCAN)
_info_cache = aiocache.SimpleMemoryCache(namespace=NS_INFO)


def configure_cache():
    """Set the configuration for the asynchronous cache used by Synse."""
    logger.debug(gettext('CONFIGURING CACHE: {}').format(config.AIOCACHE))
    aiocache.caches.set_config(config.AIOCACHE)


async def clear_cache(namespace):
    """Clear the cache with the given namespace.

    Cache namespaces are defined in the cache module as variables with
    a "NS_" prefix.

    Args:
        namespace (str): The namespace of the cache to clear.
    """
    _cache = aiocache.caches.get('default')
    return await _cache.clear(namespace=namespace)


async def clear_all_meta_caches():
    """Clear all caches which contain or are derived from meta-information
    collected from gRPC Metainfo requests.
    """
    for ns in [NS_META, NS_INFO, NS_SCAN]:
        await clear_cache(ns)


async def get_transaction(transaction_id):
    """Get the cached information relating to the given transaction.

    The cached info should include the name of the plugin from which the given
    transaction originated, and the context of the transaction.

    Args:
        transaction_id (str): The ID of the transaction.

    Returns:
        dict: The information associated with a transaction.
    """
    return await transaction_cache.get(transaction_id)


async def add_transaction(transaction_id, context, plugin_name):
    """Add a new transaction to the transactions cache.

    This cache tracks transactions and maps them to the plugin from which they
    originated, as well as the context of the transaction.

    Args:
        transaction_id (str): The ID of the transaction.
        context (dict): The action/raw data of the write transaction that
            can be used to help identify the transaction.
        plugin_name (str): The name of the plugin to associate with the
            transaction.

    Returns:
        bool: True if successful; False otherwise.
    """
    # TODO (etd): add TTL to the transactions. TBD where this timeout is
    # defined. Likely check the config for a value - if not there, use some
    # default. #397
    return await transaction_cache.set(
        transaction_id,
        {
            'plugin': plugin_name,
            'context': context
        }
    )


async def get_device_meta(rack, board, device):
    """Get the meta-information for a device.

    Args:
        rack (str): The rack which the device resides on.
        board (str): The board which the device resides on.
        device (str): The ID of the device to get meta-info for.

    Returns:
        MetainfoResponse: The meta information for the specified device.

    Raises:
        SynseError: The given rack-board-device combination does not
            correspond to a known device.
    """
    cid = utils.composite(rack, board, device)
    _cache = await get_metainfo_cache()

    dev = _cache.get(cid)

    if dev is None:
        raise errors.DeviceNotFoundError(
            gettext('{} does not correspond with a known device.').format(
                '/'.join([rack, board, device]))
        )
    return dev


async def get_metainfo_cache():
    """Get the cached meta-information aggregated from the gRPC Metainfo
    request across all plugins.

    If the cache does not exist or has surpassed its TTL, it will be
    refreshed.

    If there are no registered plugins, it attempts to re-register them.

    The metainfo cache is a map where the key is the device id composite
    and the value is the MetainfoResponse associated with that device.
    For example:
        {
          "rack1-vec-1249ab12f2ed" : <MetainfoResponse>
        }

    For the fields of the MetainfoResponse, see the gRPC proto spec:
    https://github.com/vapor-ware/synse-server-grpc/blob/master/synse.proto

    Returns:
        dict: The metainfo dictionary in which the key is the device id
            and the value is the data associated with that device.
    """
    # Get the cache and return it if it exists, otherwise, rebuild.
    value = await _meta_cache.get(META_CACHE_KEY)
    if value is not None:
        return value

    metainfo = _build_metainfo_cache()

    # If the metainfo data is empty when built, we don't want to cache an
    # empty dictionary, so we will set it to None. Future calls to get_metainfo_cache
    # will then attempt to rebuild the cache
    value = metainfo if metainfo else None

    # get meta cache's ttl and update the cache
    ttl = config.options.get('cache', {}).get('meta', {}).get('ttl', None)
    await _meta_cache.set(META_CACHE_KEY, value, ttl=ttl)

    return metainfo


async def get_scan_cache():
    """Get the cached scan results.

    If the scan result cache does not exist or the TTL has expired, the cache
    will be refreshed.

    An example of the scan cache structure:
        {
          'racks': [
            {
              'id': 'rack-1',
              'boards': [
                {
                  'id': 'vec',
                  'devices': [
                    {
                      'id': '1e93da83dd383757474f539314446c3d',
                      'info': 'Rack Temperature Spare',
                      'type': 'temperature'
                    },
                    {
                      'id': '18185208cbc0e5a4700badd6e39bb12d',
                      'info': 'Rack Temperature Middle Rear',
                      'type': 'temperature'
                    }
                  ]
                }
              ]
            }
          ]
        }

    Returns:
        dict: A dictionary containing the scan command result.
    """
    value = await _scan_cache.get(SCAN_CACHE_KEY)
    if value is not None:
        return value

    # if the cache is not found, we will (re)build it from metainfo cache
    _metainfo = await get_metainfo_cache()
    scan_cache = _build_scan_cache(_metainfo)

    # If the scan data is empty when built, we don't want to cache an empty
    # dictionary, so we will set it to None. Future calls to get_scan_cache
    # will then attempt to rebuild the cache
    value = scan_cache if scan_cache else None

    # get the scan cache's ttl and update the cache. this should be the same
    # ttl that is used by the metainfo cache.
    ttl = config.options.get('cache', {}).get('meta', {}).get('ttl', None)
    await _meta_cache.set(SCAN_CACHE_KEY, value, ttl=ttl)

    return scan_cache


async def get_resource_info_cache():
    """Get the cached resource info.

    If the resource info cache does not exist or the TTL has expired, the
    cache will be refreshed.

    An example of the info cache structure:
        {
          'rack-1': {
            'rack': 'rack-1',
            'boards': {
              'vec': {
                'board': 'vec',
                'devices': {
                  '1e93da83dd383757474f539314446c3d': {
                    'timestamp': '2017-11-16 09:16:16.578927204 -0500 EST m=+36.995086134',
                    'uid': '1e93da83dd383757474f539314446c3d',
                    'type': 'temperature',
                    'model': 'MAX11610',
                    'manufacturer': 'Maxim Integrated',
                    'protocol': 'i2c',
                    'info': 'Rack Temperature Spare',
                    'comment': '',
                    'location': {
                      'rack': 'rack-1',
                      'board': 'vec'
                    },
                    'output': [
                      {
                        'type': 'temperature',
                        'data_type': 'float',
                        'precision': 2,
                        'unit': {
                          'name': 'degrees celsius',
                          'symbol': 'C'
                        },
                        'range': {
                          'min': 0,
                          'max': 100
                        }
                      }
                    ]
                  }
                }
              }
            }
          }
        }

    Returns:
        dict: A dictionary containing the info command result.
    """
    value = await _info_cache.get(INFO_CACHE_KEY)
    if value is not None:
        return value

    # if the cache is not found, we will (re)build it from metainfo cache
    _metainfo = await get_metainfo_cache()
    info_cache = _build_resource_info_cache(_metainfo)

    # If the info data is empty when built, we don't want to cache an empty
    # dictionary, so we will set it to None. Future calls to get_info_cache
    # will then attempt to rebuild the cache
    value = info_cache if info_cache else None

    # get the info cache's ttl and update the cache. this should be the same
    # ttl that is used by the metainfo cache.
    ttl = config.options.get('cache', {}).get('meta', {}).get('ttl', None)
    await _meta_cache.set(INFO_CACHE_KEY, value, ttl=ttl)

    return info_cache


def _build_metainfo_cache():
    """Construct the dictionary that will become the metainfo cache.

    Returns:
        dict: The metainfo dictionary in which the key is the device id
            and the value is the data associated with that device.
    """
    logger.debug(gettext('Building the metainfo cache.'))
    metainfo = {}

    # first, we want to iterate through all of the known plugins and
    # use the associated client to get the meta information provided by
    # that backend.
    plugins = Plugin.manager.plugins
    if len(plugins) == 0:
        logger.debug(gettext('Manager has no plugins - registering plugins.'))
        register_plugins()
        plugins = Plugin.manager.plugins

    logger.debug(gettext('plugins to scan: {}').format(len(plugins)))

    # track which plugins failed to provide metainfo for any reason.
    failures = {}

    for name, plugin in plugins.items():
        logger.debug('{} -- {}'.format(name, plugin))

        try:
            for device in plugin.client.metainfo():
                _id = utils.composite(device.location.rack, device.location.board, device.uid)
                metainfo[_id] = device

        # we do not want to fail the scan if a single plugin fails to provide
        # meta-information.
        #
        # FIXME (etd): instead of just logging out the errors, we could either:
        #   - update the response scheme to hold an 'errors' field which will alert
        #     the user of these partial non-fatal errors.
        #   - update the API to add a url to check the currently configured plugins
        #     and their 'health'/'state'.
        #   - both
        except grpc.RpcError as ex:
            failures[name] = ex
            logger.warning(gettext('Failed to get metainfo for plugin: {}').format(name))

    # if we fail to read from all plugins (assuming there were any), then we
    # can raise an error since it is likely something is mis-configured.
    if plugins and len(plugins) == len(failures):
        raise errors.InternalApiError(
            gettext('Failed to scan all plugins: {}').format(failures)
        )

    return metainfo


def _build_scan_cache(metainfo):
    """Build the scan cache.

    This builds the scan cache, adhering to the Scan response scheme,
    using the contents of the meta-info cache.

    Args:
        metainfo (dict): The meta-info cache dictionary.

    Returns:
        dict: The constructed scan cache.
    """
    logger.debug(gettext('Building the scan cache.'))
    scan_cache = {}

    # the _tracked dictionary is used to help track which racks and
    # boards already exist while we are building the cache. it should
    # look something like:
    #
    #   _tracked = {
    #       'rack_id_1': {
    #           'rack': <>,
    #           'boards': {
    #               'board_id_1': <>,
    #               'board_id_2': <>
    #           }
    #       }
    #   }
    #
    # where we track racks by their id, map each rack to a dictionary
    # containing the rack info, and track each board on the rack under
    # the 'boards' key.
    _tracked = {}

    for source in metainfo.values():
        rack_id = source.location.rack
        board_id = source.location.board
        device_id = source.uid

        # the given rack does not yet exist in our scan cache.
        # in this case, we will create it, along with the board
        # and device that the source record provides.
        if rack_id not in _tracked:
            new_board = {
                'id': board_id,
                'devices': [
                    {
                        'id': device_id,
                        'info': source.info,
                        'type': source.type
                    }
                ]
            }

            new_rack = {
                'id': rack_id,
                'boards': []
            }

            # update the _tracked dictionary with references to the
            # newly created rack and board.
            _tracked[rack_id] = {
                'rack': new_rack,
                'boards': {
                    board_id: new_board
                }
            }

        # the rack does exist in the scan cache. in this case, we will
        # check if the board exists. if not, we will create it with the
        # device that the source record provides. if so, we will append
        # the device information provided by the source record to the
        # existing board.
        else:
            r = _tracked[rack_id]
            if board_id not in r['boards']:
                new_board = {
                    'id': board_id,
                    'devices': [
                        {
                            'id': device_id,
                            'info': source.info,
                            'type': source.type
                        }
                    ]
                }

                r['boards'][board_id] = new_board

            else:
                r['boards'][board_id]['devices'].append({
                    'id': device_id,
                    'info': source.info,
                    'type': source.type
                })

    if _tracked:
        # add the root 'racks' field to the scan data
        scan_cache['racks'] = []

        # populate the rack info and add it to the scan data racks list
        for ref in _tracked.values():
            ref['rack']['boards'] = list(ref['boards'].values())
            scan_cache['racks'].append(ref['rack'])

    return scan_cache


def _build_resource_info_cache(metainfo):
    """Build the resource info cache.

    This builds the info cache, adhering to the Info response scheme,
    using the contents of the meta-info cache.

    Args:
        metainfo (dict): The meta-info cache dictionary.

    Returns:
        dict: The constructed info cache.
    """
    logger.debug(gettext('Building the info cache.'))
    info_cache = {}

    for source in metainfo.values():

        src = putil.metainfo_to_dict(source)

        rack = source.location.rack
        board = source.location.board
        device = source.uid

        if rack in info_cache:
            rdata = info_cache[rack]
            if board in rdata['boards']:
                bdata = rdata['boards'][board]
                if device not in bdata['devices']:
                    bdata['devices'][device] = src
            else:
                rdata['boards'][board] = {
                    'board': board,
                    'devices': {device: src}
                }
        else:
            info_cache[rack] = {
                'rack': rack,
                'boards': {
                    board: {
                        'board': board,
                        'devices': {device: src}
                    }
                }
            }

    return info_cache
