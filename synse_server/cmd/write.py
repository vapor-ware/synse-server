
from synse_server import cache, plugin
from synse_server.log import logger
from synse_server.i18n import _


async def write_async(device_id, payload):
    """Generate the asynchronous write response data.

    Args:
        device_id (str): The ID of the device to write to.
        payload (dict | list[dict]): The data to write to the device.

    Returns:
        list[dict]: A list of dictionary representations of asynchronous
        write response(s).
    """
    logger.debug(_('issuing command'), command='WRITE ASYNC')

    # FIXME: This is a common pattern - consider making a util (get_plugin_for_device)
    device = await cache.get_device(device_id)
    if not device:
        # todo: raise proper error
        raise ValueError

    p = plugin.manager.get(device.plugin)
    if not p:
        # todo: raise proper error
        raise ValueError

    # TODO: add the transaction to the cache

    return p.client.write_async(
        device_id=device_id,
        data=payload,
    )


async def write_sync(device_id, payload):
    """Generate the synchronous write response data.

    Args:
        device_id (str): The ID of the device to write to.
        payload (dict | list[dict]): The data to write to the device.

    Returns:
        list[dict]: A list of dictionary representations of synchronous
        write response(s).
    """
    logger.debug(_('issuing command'), command='WRITE SYNC')

    device = await cache.get_device(device_id)
    if not device:
        # todo: raise proper error
        raise ValueError

    p = plugin.manager.get(device.plugin)
    if not p:
        # todo: raise proper error
        raise ValueError

    return p.client.write_sync(
        device_id=device_id,
        data=payload,
    )
