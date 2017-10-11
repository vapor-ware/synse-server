"""

"""

import aiocache
import grpc

from synse import errors
from synse.log import logger
from synse.proc import BGProc, get_procs

NS_TRANSACTION = 'transaction'
NS_META = 'meta'
NS_SCAN = 'scan'
NS_INFO = 'info'
NS_LDMAP = 'ldmap'


# FIXME -- the TTL here should probably be longer and configured
# separately from the other ttls.
transaction_cache = aiocache.SimpleMemoryCache(namespace=NS_TRANSACTION)


async def clear_cache(namespace):
    """

    Args:
        namespace (str):
    """
    _cache = aiocache.caches.get('default')
    return await _cache.clear(namespace=namespace)


async def clear_all_meta_caches():
    """
    """
    for ns in [NS_META, NS_INFO, NS_SCAN, NS_LDMAP]:
        await clear_cache(ns)


async def get_transaction(transaction_id):
    """

    Args:
        transaction_id (str):
    """
    return await transaction_cache.get(transaction_id)


async def add_transaction(transaction_id, process_name):
    """

    Args:
        transaction_id (str):
        process_name (str):

    Returns:
        bool
    """
    return await transaction_cache.set(transaction_id, process_name)


@aiocache.cached(ttl=20, namespace=NS_META)
async def get_metainfo_cache():
    """
    """
    metainfo = {}

    # first, we want to iterate through all of the known background processes
    # and use the associated client to get the meta information provided by
    # that backend.

    logger.debug('process: {}'.format(BGProc.manager.processes))

    for name, proc in get_procs():
        logger.debug('{} -- {}'.format(name, proc))

        try:
            for device in proc.client.metainfo():
                _id = device.uid

                metainfo[_id] = device

        # FIXME - do we want to outright fail if we cant reach one of the
        #   background processes, or continue on and resolve all that we
        #   are able to? for now, failing hard since that is simplest.
        except grpc.RpcError as ex:
            raise errors.SynseError('Failed to get metainfo for process "{}"'.format(name), errors.INTERNAL_API_FAILURE) from ex

    logger.debug('Got metainfo cache!')
    return metainfo


@aiocache.cached(ttl=20, namespace=NS_LDMAP)
async def get_location_device_map():
    """

    the location-device map maps the devices based on location.
    this is used as a lookup table for routes, which recieve
    rack/board/device, to translate to the device uid.
    """
    meta_cache = await get_metainfo_cache()

    ld_map = {}
    for uid, dev in meta_cache.items():
        rack = dev.location.rack
        board = dev.location.board
        device = dev.location.device

        if rack not in ld_map:
            ld_map[rack] = {board: {device: uid}}

        else:
            ld_rack = ld_map[rack]
            if board not in ld_rack:
                ld_map[rack][board] = {device: uid}

            else:
                ld_board = ld_rack[board]
                if device not in ld_board:
                    ld_map[rack][board][device] = uid

    return ld_map


@aiocache.cached(ttl=20, namespace=NS_SCAN)
async def get_scan_cache():
    """
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
    """
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
        device = source.location.device

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
