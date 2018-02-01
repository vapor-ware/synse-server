"""Synse Server caches and cache utilities.
"""

import aiocache
import grpc

from synse import errors, utils
from synse.config import AIOCACHE
from synse.log import logger
from synse.plugin import Plugin, register_plugins
from synse.proto import util as putil

NS_TRANSACTION = 'transaction'
NS_META = 'meta'
NS_SCAN = 'scan'
NS_INFO = 'info'


# FIXME -- the TTL here should probably be longer and configured
# separately from the other ttls.
transaction_cache = aiocache.SimpleMemoryCache(namespace=NS_TRANSACTION)


def configure_cache():
    """Set the configuration for the asynchronous cache used by Synse."""
    logger.debug(gettext('CONFIGURING CACHE: {}').format(AIOCACHE))
    aiocache.caches.set_config(AIOCACHE)


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
        raise errors.SynseError(
            gettext('{} does not correspond with a known device.').format(
                '/'.join([rack, board, device])), errors.DEVICE_NOT_FOUND
        )
    return dev


@aiocache.cached(ttl=20, namespace=NS_META)
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
    metainfo = {}

    # first, we want to iterate through all of the known background processes
    # and use the associated client to get the meta information provided by
    # that backend.

    plugins = Plugin.manager.plugins

    if len(plugins) == 0:
        logger.debug(gettext('Re-registering plugins.'))
        register_plugins()
        plugins = Plugin.manager.plugins

    logger.debug(gettext('plugins to scan: {}').format(plugins))

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
        raise errors.SynseError(
            gettext('Failed to scan all plugins: {}').format(failures),
            errors.INTERNAL_API_FAILURE
        )

    logger.debug(gettext('Got metainfo cache!'))
    return metainfo


@aiocache.cached(ttl=20, namespace=NS_SCAN)
async def get_scan_cache():
    """Get the cached scan results.

    If the scan result cache does not exist or the TTL has expired, the cache
    will be refreshed.

    An example of the scan cache structure:
        {
          'racks': [
            {
              'rack_id': 'rack-1',
              'boards': [
                {
                  'board_id': 'vec',
                  'devices': [
                    {
                      'device_id': '1e93da83dd383757474f539314446c3d',
                      'device_info': 'Rack Temperature Spare',
                      'device_type': 'temperature'
                    },
                    {
                      'device_id': '18185208cbc0e5a4700badd6e39bb12d',
                      'device_info': 'Rack Temperature Middle Rear',
                      'device_type': 'temperature'
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
    logger.debug(gettext('Getting scan metainfo cache for scancache'))
    _metainfo = await get_metainfo_cache()
    logger.debug(gettext('Building scan cache.'))
    scan_cache = build_scan_cache(_metainfo)
    return scan_cache


@aiocache.cached(ttl=20, namespace=NS_INFO)
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
    _metainfo = await get_metainfo_cache()
    info_cache = build_resource_info_cache(_metainfo)
    return info_cache


def build_scan_cache(metainfo):
    """Build the scan cache.

    This builds the scan cache, adhering to the Scan response scheme,
    using the contents of the meta-info cache.

    Args:
        metainfo (dict): The meta-info cache dictionary.

    Returns:
        dict: The constructed scan cache.
    """

    scan_cache = {'racks': []}

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
        rack = source.location.rack
        board = source.location.board
        device = source.uid

        # the given rack does not yet exist in our scan cache.
        # in this case, we will create it, along with the board
        # and device that the source record provides.
        if rack not in _tracked:
            new_board = {
                'board_id': board,
                'devices': [
                    {
                        'device_id': device,
                        'device_info': source.info,
                        'device_type': source.type
                    }
                ]
            }

            new_rack = {
                'rack_id': rack,
                'boards': []
            }

            # update the _tracked dictionary with references to the
            # newly created rack and board.
            _tracked[rack] = {
                'rack': new_rack,
                'boards': {
                    board: new_board
                }
            }

        # the rack does exist in the scan cache. in this case, we will
        # check if the board exists. if not, we will create it with the
        # device that the source record provides. if so, we will append
        # the device information provided by the source record to the
        # existing board.
        else:
            r = _tracked[rack]
            if board not in r['boards']:
                new_board = {
                    'board_id': board,
                    'devices': [
                        {
                            'device_id': device,
                            'device_info': source.info,
                            'device_type': source.type
                        }
                    ]
                }

                r['boards'][board] = new_board

            else:
                r['boards'][board]['devices'].append({
                    'device_id': device,
                    'device_info': source.info,
                    'device_type': source.type
                })

    for ref in _tracked.values():
        ref['rack']['boards'] = list(ref['boards'].values())
        scan_cache['racks'].append(ref['rack'])

    return scan_cache


def build_resource_info_cache(metainfo):
    """Build the resource info cache.

    This builds the info cache, adhering to the Info response scheme,
    using the contents of the meta-info cache.

    Args:
        metainfo (dict): The meta-info cache dictionary.

    Returns:
        dict: The constructed info cache.
    """
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
