
import grpc
import synse_grpc.utils

from synse_server import cache, plugin
from synse_server.log import logger
from synse_server.i18n import _


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

    devices = await cache.get_devices(*tags)
    logger.debug(_('retrieved devices matching tag(s)'), devices=len(devices), tags=tags)

    readings = []
    for device in devices:
        p = plugin.manager.get(device.plugin)
        if not p:
            # todo: raise proper error
            raise ValueError

        try:
            data = p.client.read(tags=tags)
        except grpc.RpcError as e:
            # todo: raise proper error
            raise ValueError from e

        for reading in data:
            readings.append(synse_grpc.utils.to_dict(reading))

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

    device = await cache.get_device(device_id)
    if not device:
        # todo: raise proper error
        raise ValueError

    p = plugin.manager.get(device.plugin)
    if not p:
        # todo: raise proper error
        raise ValueError

    readings = []
    try:
        data = p.client.read(device_id=device_id)
    except grpc.RpcError as e:
        # todo: raise proper error
        raise ValueError from e

    for reading in data:
        readings.append(synse_grpc.utils.to_dict(reading))

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

    for p in plugin.manager:
        logger.debug(_('getting cached readings for plugin'), plugin=p.tag)
        for reading in p.client.read_cache(start=start, end=end):
            yield synse_grpc.utils.to_dict(reading)
