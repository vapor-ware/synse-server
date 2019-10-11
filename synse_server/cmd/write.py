
from synse_grpc import utils

from synse_server import cache, errors
from synse_server.i18n import _
from synse_server.log import logger


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

    plugin = await cache.get_plugin(device_id)
    if plugin is None:
        raise errors.NotFound(
            _('plugin not found for device {}').format(device_id),
        )

    response = []
    try:
        with plugin as client:
            for txn in client.write_async(device_id=device_id, data=payload):
                # Add the transaction to the cache
                await cache.add_transaction(txn.id, txn.device, plugin.id)
                rsp = utils.to_dict(txn)
                if rsp.get('context', {}).get('data'):
                    rsp['context']['data'] = rsp['context']['data'].decode('utf-8')
                response.append(rsp)
    except Exception as e:
        raise errors.ServerError(
            _('error while issuing gRPC request: async write'),
        ) from e

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

    plugin = await cache.get_plugin(device_id)
    if plugin is None:
        raise errors.NotFound(
            _('plugin not found for device {}').format(device_id),
        )

    response = []
    try:
        with plugin as client:
            for status in client.write_sync(device_id=device_id, data=payload):
                # Add the transaction to the cache
                await cache.add_transaction(status.id, device_id, plugin.id)
                s = utils.to_dict(status)
                s['device'] = device_id
                if s.get('context', {}).get('data'):
                    s['context']['data'] = s['context']['data'].decode('utf-8')
                response.append(s)
    except Exception as e:
        raise errors.ServerError(
            _('error while issuing gRPC request: sync write'),
        ) from e

    return response
