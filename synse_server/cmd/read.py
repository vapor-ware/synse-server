
import synse_grpc.utils

from synse_server import cache, errors, plugin
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
            # fixme: value should be under "value" key, not the OneOf type key
            # fixme: need device ID
            # fixme: need device type
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

    p = await cache.get_plugin(device_id)
    if p is None:
        raise errors.NotFound(
            _(f'plugin not found for device {device_id}'),
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
        # fixme: value should be under "value" key, not the OneOf type key
        # fixme: need device ID
        # fixme: need device type
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
        try:
            for reading in p.client.read_cache(start=start, end=end):
                yield synse_grpc.utils.to_dict(reading)
            p.mark_active()
        except Exception as e:
            # FIXME: this should be a client connection error, as defined by the
            #   grpc client package
            p.mark_inactive()
            raise
