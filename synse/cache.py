"""Synse Server caches and cache utilities.
"""

import aiocache
import grpc

from synse import errors, utils
from synse.log import logger
from synse.plugin import Plugin, get_plugins

NS_TRANSACTION = 'transaction'
NS_META = 'meta'
NS_SCAN = 'scan'
NS_INFO = 'info'


# FIXME -- the TTL here should probably be longer and configured
# separately from the other ttls.
transaction_cache = aiocache.SimpleMemoryCache(namespace=NS_TRANSACTION)


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


async def get_transaction_plugin(transaction_id):
    """Get the name of the plugin from which the given transaction originated.

    Args:
        transaction_id (str): The ID of the transaction.

    Returns:
        str: The name of the plugin tracking the transaction.
    """
    return await transaction_cache.get(transaction_id)


async def add_transaction(transaction_id, plugin_name):
    """Add a new transaction to the transactions cache.

    This cache tracks transactions and maps them to the plugin from which they
    originated.

    Args:
        transaction_id (str): The ID of the transaction.
        plugin_name (str): The name of the plugin to associate with the
            transaction.

    Returns:
        bool: True if successful; False otherwise.
    """
    return await transaction_cache.set(transaction_id, plugin_name)


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
            '{} does not correspond with a known device.'.format(
                '/'.join([rack, board, device]), errors.DEVICE_NOT_FOUND)
        )
    return dev


@aiocache.cached(ttl=20, namespace=NS_META)
async def get_metainfo_cache():
    """Get the cached meta-information aggregated from the gRPC Metainfo
    request across all plugins.

    If the cache does not exist or has surpassed its TTL, it will be
    refreshed.

    Returns:
        dict: The metainfo dictionary in which the key is the device id
            and the value is the data associated with that device.
    """
    metainfo = {}

    # first, we want to iterate through all of the known background processes
    # and use the associated client to get the meta information provided by
    # that backend.

    logger.debug('plugins: {}'.format(Plugin.manager.plugins))

    for name, plugin in get_plugins():
        logger.debug('{} -- {}'.format(name, plugin))

        try:
            for device in plugin.client.metainfo():
                _id = utils.composite(device.location.rack, device.location.board, device.uid)
                metainfo[_id] = device

        # FIXME - do we want to outright fail if we cant reach one of the
        #   background processes, or continue on and resolve all that we
        #   are able to? for now, failing hard since that is simplest.
        except grpc.RpcError as ex:
            raise errors.SynseError('Failed to get metainfo for process "{}"'.format(name), errors.INTERNAL_API_FAILURE) from ex

    logger.debug('Got metainfo cache!')
    return metainfo


@aiocache.cached(ttl=20, namespace=NS_SCAN)
async def get_scan_cache():
    """Get the cached scan results.

    If the scan result cache does not exist or the TTL has expired, the cache
    will be refreshed.

    Returns:
        dict: A dictionary containing the scan command result.
    """
    logger.debug('aiocache cache config:')
    logger.debug(aiocache.caches._config)
    logger.debug('Getting scan metainfo cache for scancache')
    _metainfo = await get_metainfo_cache()
    logger.debug('Building scan cache.')
    scan_cache = build_scan_cache(_metainfo)
    return scan_cache


@aiocache.cached(ttl=20, namespace=NS_INFO)
async def get_resource_info_cache():
    """Get the cached resource info.

    If the resource info cache does not exist or the TTL has expired, the
    cache will be refreshed.

    Returns:
        dict:
    """
    _metainfo = await get_metainfo_cache()
    info_cache = build_resource_info_cache(_metainfo)
    return info_cache


# FIXME - I think this should move to the 'commands.scan' module?
#   or maybe not? just trying to keep command specific things isolated
#   to those specific commands.
def build_scan_cache(metainfo):
    """

    Args:
        metainfo (dict):
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

        # FIXME: before, this was source.location.device -- need to spend some
        # more time thinking about/designing out the world of IDs in our system.
        # does the device id belong in the location? is there (or should there be)
        # a difference between the internal UID and the id shown to the user?
        # probably more questions surrounding this, but that's a start.
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
        ref['rack']['boards'] = ref['boards'].values()
        scan_cache['racks'].append(ref['rack'])

    return scan_cache


# TODO - what should this even be?
def build_resource_info_cache(metainfo):
    """

    Args:
        metainfo (dict):
    """
    info_cache = {'info': []}

    for source in metainfo.values():
        rack = source.location.rack
        board = source.location.board
        device = source.location.device

        info_cache['info'].append({'r': rack, 'b': board, 'd': device})

    return info_cache
