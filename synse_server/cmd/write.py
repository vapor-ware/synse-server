
from typing import Any, Dict, List, Union

from structlog import get_logger
from synse_grpc import utils as grpc_utils

from synse_server import cache, errors, utils

logger = get_logger()


async def write_async(device_id: str, payload: Union[Dict, List[Dict]]) -> List[Dict[str, Any]]:
    """Generate the asynchronous write response data.

    Args:
        device_id: The ID of the device to write to.
        payload: The data to write to the device.

    Returns:
        A list of dictionary representations of asynchronous write response(s).
    """
    logger.info(
        'issuing command',
        command='WRITE ASYNC', device_id=device_id, payload=payload,
    )

    plugin = await cache.get_plugin(device_id)
    if plugin is None:
        raise errors.NotFound(
            f'plugin not found for device {device_id}',
        )

    response = []
    try:
        with plugin as client:
            for txn in client.write_async(device_id=device_id, data=payload):
                # Add the transaction to the cache
                await cache.add_transaction(txn.id, txn.device, plugin.id)
                rsp = grpc_utils.to_dict(txn)
                utils.normalize_write_ctx(rsp)
                response.append(rsp)
    except Exception as e:
        raise errors.ServerError(
            'error while issuing gRPC request: async write',
        ) from e

    return response


async def write_sync(device_id: str, payload: Union[Dict, List[Dict]]) -> List[Dict[str, Any]]:
    """Generate the synchronous write response data.

    Args:
        device_id: The ID of the device to write to.
        payload: The data to write to the device.

    Returns:
        A list of dictionary representations of synchronous write response(s).
    """
    logger.info(
        'issuing command',
        command='WRITE SYNC', device_id=device_id, payload=payload,
    )

    plugin = await cache.get_plugin(device_id)
    if plugin is None:
        raise errors.NotFound(
            f'plugin not found for device {device_id}',
        )

    response = []
    try:
        with plugin as client:
            for status in client.write_sync(device_id=device_id, data=payload):
                # Add the transaction to the cache
                await cache.add_transaction(status.id, device_id, plugin.id)
                s = grpc_utils.to_dict(status)
                s['device'] = device_id
                utils.normalize_write_ctx(s)
                response.append(s)
    except Exception as e:
        raise errors.ServerError(
            'error while issuing gRPC request: sync write',
        ) from e

    return response
