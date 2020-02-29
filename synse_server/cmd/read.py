
import asyncio
import queue
import threading
from typing import Any, AsyncIterable, Dict, List, Union

import synse_grpc.utils
import websockets
from structlog import get_logger
from synse_grpc import api

from synse_server import cache, errors, plugin

logger = get_logger()


def reading_to_dict(reading: api.V3Reading) -> Dict[str, Any]:
    """Convert a V3Reading to its dict representation for the Synse V3 read schema.

    Args:
        reading: The reading value received from a plugin.

    Returns:
        The reading converted to its dictionary representation, conforming
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


async def read(ns: str, tag_groups: Union[List[str], List[List[str]]]) -> List[Dict[str, Any]]:
    """Generate the readings response data.

    Args:
        ns: The default namespace to use for tags which do no specify one.
            If all tags specify a namespace, or no tags are defined, this
            is ignored.
        tag_groups: The tags groups used to filter devices. If no tag
            groups are given (and thus no tags), no filtering is done.

    Returns:
        A list of dictionary representations of device reading response(s).
    """
    logger.info('issuing command', command='READ', ns=ns, tag_groups=tag_groups)

    # If there are no tags specified, read with no tag filter.
    if len(tag_groups) == 0:
        logger.debug('no tags specified, reading with no tag filter', command='READ')
        readings = []
        for p in plugin.manager:
            if not p.active:
                logger.debug(
                    'plugin not active, will not read its devices',
                    plugin=p.tag, plugin_id=p.id,
                )
                continue

            try:
                with p as client:
                    data = client.read()
            except Exception as e:
                raise errors.ServerError(
                    'error while issuing gRPC request: read'
                ) from e
            for reading in data:
                readings.append(reading_to_dict(reading))
        logger.debug('got readings', count=len(readings), command='READ')
        return readings

    # Otherwise, there is at least one tag group. We need to issue a read request
    # for each group and collect the results of each group. The provided tag groups
    # may take the form of a List[str] in the case of a single tag group, or a
    # List[List[str]] in the case of multiple tag groups.
    if all(isinstance(x, str) for x in tag_groups):
        tag_groups = [tag_groups]

    results = {}
    for group in tag_groups:
        logger.debug('parsing tag groups', command='READ', group=group)
        # Apply the default namespace to the tags in the group which do not
        # have any namespace defined.
        for i, tag in enumerate(group):
            if '/' not in tag:
                group[i] = f'{ns}/{tag}'

        for p in plugin.manager:
            if not p.active:
                logger.debug(
                    'plugin not active, will not read its devices',
                    plugin=p.tag, plugin_id=p.id,
                )
                continue

            try:
                with p as client:
                    data = client.read(tags=group)
            except Exception as e:
                raise errors.ServerError(
                    'error while issuing gRPC request: read'
                ) from e

            for r in data:
                results[f'{r.id}{r.type}{r.timestamp}'] = reading_to_dict(r)

    readings = list(results.values())
    logger.debug('got readings', count=len(readings), command='READ')
    return readings


async def read_device(device_id: str) -> List[Dict[str, Any]]:
    """Generate the readings response data for the specified device.

    Args:
        device_id: The ID of the device to get readings for.

    Returns:
        A list of dictionary representations of device reading response(s).
    """
    logger.info('issuing command', command='READ DEVICE', device_id=device_id)

    p = await cache.get_plugin(device_id)
    if p is None:
        raise errors.NotFound(
            f'plugin not found for device {device_id}',
        )

    readings = []
    try:
        with p as client:
            data = client.read(device_id=device_id)
    except Exception as e:
        raise errors.ServerError(
            'error while issuing gRPC request: read device',
        ) from e

    for reading in data:
        readings.append(reading_to_dict(reading))

    logger.debug('got readings', count=len(readings), command='READ DEVICE')
    return readings


async def read_cache(start: str = None, end: str = None) -> AsyncIterable:
    """Generate the readings response data for the cached readings.

    Args:
        start: An RFC3339 formatted timestamp defining the starting
            bound on the cache data to return. An empty string or None
            designates no starting bound. (default: None)
        end: An RFC3339 formatted timestamp defining the ending
            bound on the cache data to return. An empty string or None
            designates no ending bound. (default: None)

    Yields:
        A dictionary representation of a device reading response.
    """
    logger.info('issuing command', command='READ CACHE', start=start, end=end)

    # FIXME: this could benefit from being async
    for p in plugin.manager:
        if not p.active:
            logger.debug(
                'plugin not active, will not read its devices',
                plugin=p.tag, plugin_id=p.id,
            )
            continue

        logger.debug('getting cached readings for plugin', plugin=p.tag, command='READ CACHE')
        try:
            with p as client:
                for reading in client.read_cache(start=start, end=end):
                    yield reading_to_dict(reading)
        except Exception as e:
            raise errors.ServerError(
                'error while issuing gRPC request: read cache',
            ) from e


class Stream(threading.Thread):
    """A thread which streams reading data from a plugin.

    The reading data received from the plugin is put onto the thread-safe
    queue specified on initialization.

    Args:
        plugin: The plugin to gather reading data from.
        ids: A list of device IDs which can be used to constrain the devices
            for which readings should be streamed.
        tag_groups: A collection of tag groups to constrain the devices for
            which readings should be streamed. The tags within a group are
            subtractive (e.g. a device must match all tags in the group to
            match the filter), but each tag group specified is additive (e.g.
            readings will be streamed for the union of all specified groups).
        q: The thread-safe queue to pass collected readings to.
    """

    def __init__(
            self,
            plugin: plugin.Plugin,
            ids: List[str],
            tag_groups: List[List[str]],
            q: queue.Queue,
    ) -> None:
        super(Stream, self).__init__()
        self.plugin = plugin
        self.q = q
        self.ids = ids
        self.tag_groups = tag_groups
        self.event = threading.Event()

    def run(self) -> None:
        """Run the thread."""
        logger.info('running Stream thread', plugin=self.plugin.id)
        try:
            with self.plugin as client:
                for reading in client.read_stream(devices=self.ids, tag_groups=self.tag_groups):
                    self.q.put(reading_to_dict(reading))

                    # Important: we need to check if the thread event is set -- this
                    # allows the thread to be cancellable.
                    if self.event.is_set():
                        logger.info('stream thread cancelled', plugin=self.plugin.id)
                        break

        except Exception as e:
            raise errors.ServerError(
                'error while issuing gRPC request: read stream',
            ) from e

    def cancel(self) -> None:
        """Cancel the thread."""
        logger.info('cancelling reading stream', plugin=self.plugin.id)
        self.event.set()


async def read_stream(
        ws: websockets.WebSocketCommonProtocol,
        ids: List[str] = None,
        tag_groups: List[List[str]] = None,
) -> AsyncIterable:
    """Stream reading data from registered plugins for the provided websocket.

    Note that this will only work for the Synse WebSocket API as of v3.0.

    Args:
        ws: The WebSocket for the request. Note that this command only works
            with the WebSocket API as of v3.0
        ids: A list of device IDs which can be used to constrain the devices
            for which readings should be streamed. If no IDs are specified, no
            filtering by ID is done.
        tag_groups: A collection of tag groups to constrain the devices for which
            readings should be streamed. The tags within a group are subtractive
            (e.g. a device must match all tags in the group to match the filter),
            but each tag group specified is additive (e.g. readings will be
            streamed for the union of all specified groups). If no tag groups are
            specified, no filtering by tags is done.

    Yields:
        The device reading, formatted as a Python dictionary.
    """

    logger.info('issuing command', command='READ STREAM', ids=ids, tag_groups=tag_groups)

    q = queue.Queue()

    threads = []
    for p in plugin.manager:
        if not p.active:
            logger.debug(
                'plugin not active, will not read its devices',
                plugin=p.tag, plugin_id=p.id,
            )
            continue

        t = Stream(p, ids, tag_groups, q)
        t.start()
        threads.append(t)

    def close_callback(*args, **kwargs):
        logger.debug('executing callback to cancel read stream threads')
        for stream in threads:
            stream.cancel()

    # The websocket has a 'close_connection_task' which will run once the
    # data transfer task as completed or been cancelled. This task should
    # always be run in the lifecycle of the websocket. We attach a callback
    # to the task to terminate the stream threads associated with the request,
    # therefore terminating the synse-server<->plugin(s) stream when the
    # client<->synse-server websocket is closed.
    ws.close_connection_task.add_done_callback(close_callback)

    logger.debug('collecting streamed readings...')
    try:
        while True:
            # Needed as an async break point in the loop, particularly for
            # cancelling the async task.
            await asyncio.sleep(0)
            try:
                val = q.get_nowait() or None
            except queue.Empty:
                await asyncio.sleep(0.25)
                continue
            else:
                if val is not None:
                    yield val
    finally:
        # The above should run until either the task is cancelled or there is
        # an exception. In either case, make the threads are terminated prior
        # to returning from this function so we are not constantly streaming
        # readings in the background.
        close_callback()
