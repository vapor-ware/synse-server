
import threading
import queue

import synse_grpc.utils

from synse_server import cache, errors, plugin
from synse_server.i18n import _
from synse_server.log import logger


def reading_to_dict(reading):
    """Convert a V3Reading to its dict representation for the Synse V3 read schema.

    Args:
        reading (V3Reading): The reading value received from a plugin.

    Returns:
        dict: The reading converted to its dictionary representation, conforming
        to the V3 API read schema.
    """
    # The reading value is stored in a protobuf oneof block - we need to
    # figure out which field it is so we can extract it. If no field is set,
    # take the reading value to be None.
    value = None
    field = reading.WhichOneof('value')
    if field is not None:
        value = getattr(reading, field)

    if not reading.unit or (reading.unit.symbol == '' and reading.unit.name == ''):
        unit = None
    else:
        unit = synse_grpc.utils.to_dict(reading.unit)

    return {
        'device': reading.id,
        'timestamp': reading.timestamp,
        'type': reading.type,
        'device_type': reading.deviceType,
        'unit': unit,
        'value': value,
        'context': dict(reading.context),
    }


async def read(ns, tags):
    """Generate the readings response data.

    Args:
        ns (str): The default namespace to use for tags which do not
            specify one. If all tags specify a namespace, or no tags
            are defined, this is ignored.
        tags (list[str]): The tags to filter devices on. If no tags are
            given, no filtering is done.

    Returns:
        list[dict]: A list of dictionary representations of device reading
        response(s).
    """
    logger.debug(_('issuing command'), command='READ', ns=ns, tags=tags)

    # Apply the default namespace to the tags which do not have any
    # namespaces, if any are defined.
    for i, tag in enumerate(tags):
        if '/' not in tag:
            tags[i] = f'{ns}/{tag}'

    readings = []
    for p in plugin.manager:
        try:
            with p as client:
                data = client.read(tags=tags)
        except Exception as e:
            raise errors.ServerError(
                _('error while issuing gRPC request: read')
            ) from e

        for reading in data:
            readings.append(reading_to_dict(reading))

    return readings


async def read_device(device_id):
    """Generate the readings response data for the specified device.

    Args:
        device_id (str): The ID of the device to get readings for.

    Returns:
        list[dict]: A list of dictionary representations of device reading
        response(s).
    """
    logger.debug(_('issuing command'), command='READ DEVICE', device_id=device_id)

    p = await cache.get_plugin(device_id)
    if p is None:
        raise errors.NotFound(
            _('plugin not found for device {}').format(device_id),
        )

    readings = []
    try:
        with p as client:
            data = client.read(device_id=device_id)
    except Exception as e:
        raise errors.ServerError(
            _('error while issuing gRPC request: read device'),
        ) from e

    for reading in data:
        readings.append(reading_to_dict(reading))

    return readings


async def read_cache(start=None, end=None):
    """Generate the readings response data for the cached readings.

    Args:
        start (str): An RFC3339 formatted timestamp defining the starting
            bound on the cache data to return. An empty string or None
            designates no starting bound. (default: None)
        end (str): An RFC3339 formatted timestamp defining the ending
            bound on the cache data to return. An empty string or None
            designates no ending bound. (default: None)

    Yields:
        dict: A dictionary representation of a device reading response.
    """
    logger.debug(_('issuing command'), command='READ CACHE', start=start, end=end)

    # FIXME: this could benefit from being async
    for p in plugin.manager:
        logger.debug(_('getting cached readings for plugin'), plugin=p.tag)
        try:
            with p as client:
                for reading in client.read_cache(start=start, end=end):
                    yield reading_to_dict(reading)
        except Exception as e:
            raise errors.ServerError(
                _('error while issuing gRPC request: read cache'),
            ) from e


async def read_stream(ids=None, tag_groups=None):
    """"""

    logger.debug(_('issuing command'), command='READ STREAM', ids=ids, tag_groups=tag_groups)

    q = queue.Queue()

    def stream(p):
        try:
            with p as client:
                for reading in client.read_stream(devices=ids, tag_groups=tag_groups):
                    q.put(reading_to_dict(reading))
        except Exception as e:
            raise errors.ServerError(
                _('error while issuing gRPC request: read stream'),
            ) from e

    threads = []
    for p in plugin.manager:
        t = threading.Thread(target=stream, args=(p,))
        t.start()
        threads.append(t)

    # TODO: figure out what the best way would be to terminate this from running forever...
    while True:
        val = None
        try:
            val = q.get_nowait()
        except queue.Empty:
            pass

        joined = 0
        for t in threads:
            t.join(timeout=0.1)
            if not t.is_alive():
                joined += 1
        if len(threads) == joined:
            break

        if val is not None:
            yield val

    # # fixme - we will need to collect from all plugins simultaneously, not one at a time
    # #   or else this wont work
    #
    # async for p in plugin.manager:
    #     try:
    #         with p as client:
    #             async for reading in client.read_stream(devices=ids, tag_groups=tag_groups):
    #                 logger.debug('streamed reading', id=reading.id, plugin=p.address)
    #                 yield reading_to_dict(reading)
    #     except Exception as e:
    #         raise errors.ServerError(
    #             _('error while issuing gRPC request: read stream'),
    #         ) from e
