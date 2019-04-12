
from synse_grpc import utils

from synse_server import cache, errors, plugin
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
    if device is None:
        raise errors.NotFound(
            f'device not found: {device_id}',
        )

    p = plugin.manager.get(device.plugin)
    if not p:
        raise errors.NotFound(
            f'plugin not found for device: {device.plugin}',
        )

    response = []
    # fixme: exception handling
    with p as client:
        for txn in client.write_async(device_id=device_id, data=payload):
            # Add the transaction to the cache
            await cache.add_transaction(txn.id, txn.device, p.id)
            response.append(utils.to_dict(txn))

    return response


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
    if device is None:
        raise errors.NotFound(
            f'device not found: {device_id}',
        )

    p = plugin.manager.get(device.plugin)
    if not p:
        raise errors.NotFound(
            f'plugin not found for device: {device.plugin}',
        )

    response = []
    # fixme: exception handling
    with p as client:
        for status in client.write_sync(device_id=device_id, data=payload):
            s = utils.to_dict(status)
            s['device'] = device_id
            response.append(s)

    return response
