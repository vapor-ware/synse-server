
import asyncio
import queue
import threading

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


class Stream(threading.Thread):
    """A thread which streams reading data from a plugin.

    The reading data received from the plugin is put onto the thread-safe
    queue specified on initialization.

    Args:
        plugin (Plugin): The plugin to gather reading data from.
        ids (list[str]): A list of device IDs which can be used to constrain
            the devices for which readings should be streamed.
        tag_groups (Iterable[list[string]]): A collection of tag groups to
            constrain the devices for which readings should be streamed. The
            tags within a group are subtractive (e.g. a device must match all
            tags in the group to match the filter), but each tag group specified
            is additive (e.g. readings will be streamed for the union of all
            specified groups).
        q (queue.Queue): The thread-safe queue to pass collected readings to.
    """

    def __init__(self, plugin, ids, tag_groups, q):
        super(Stream, self).__init__()
        self.plugin = plugin
        self.q = q
        self.ids = ids
        self.tag_groups = tag_groups
        self.event = threading.Event()

    def run(self):
        """Run the thread."""
        try:
            with self.plugin as client:
                for reading in client.read_stream(devices=self.ids, tag_groups=self.tag_groups):
                    # FIXME (etd): remove -- keeping this in for debugging during dev
                    logger.debug('streaming reading', plugin=self.plugin.id, reading=reading.id)
                    self.q.put(reading_to_dict(reading))

                    # Important: we need to check if the thread event is set -- this
                    # allows the thread to be cancellable.
                    if self.event.is_set():
                        logger.info(_('stream thread cancelled'), plugin=self.plugin.id)
                        break

        except Exception as e:
            raise errors.ServerError(
                _('error while issuing gRPC request: read stream'),
            ) from e

    def cancel(self):
        """Cancel the thread."""
        logger.info(_('cancelling reading stream'), plugin=self.plugin.id)
        self.event.set()


async def read_stream(ws, ids=None, tag_groups=None):
    """Stream reading data from registered plugins for the provided websocket.

    Note that this will only work for websockets as of v3.0.

    Args:
        ws (websockets.WebSocketCommonProtocol): The WebSocket for the request.
            Note that this command only works with the WebSocket API as of v3.0
        ids (list[str]): A list of device IDs which can be used to constrain
            the devices for which readings should be streamed. If no IDs are
            specified, no filtering by ID is done.
        tag_groups (Iterable[list[string]]): A collection of tag groups to
            constrain the devices for which readings should be streamed. The
            tags within a group are subtractive (e.g. a device must match all
            tags in the group to match the filter), but each tag group specified
            is additive (e.g. readings will be streamed for the union of all
            specified groups). If no tag groups are specified, no filtering by
            tags is done.

    Yields:
        dict: The device reading, formatted as a Python dictionary.
    """

    logger.debug(_('issuing command'), command='READ STREAM', ids=ids, tag_groups=tag_groups)

    q = queue.Queue()

    threads = []
    for p in plugin.manager:
        t = Stream(p, ids, tag_groups, q)
        t.start()
        threads.append(t)

    def close_callback(*args, **kwargs):
        logger.debug(_('executing callback to cancel read stream threads'))
        for stream in threads:
            stream.cancel()

    # The websocket has a 'close_connection_task' which will run once the
    # data transfer task as completed or been cancelled. This task should
    # always be run in the lifecycle of the websocket. We attach a callback
    # to the task to terminate the stream threads associated with the request,
    # therefore terminating the synse-server<->plugin(s) stream when the
    # client<->synse-server websocket is closed.
    ws.close_connection_task.add_done_callback(close_callback)

    logger.debug(_('collecting streamed readings...'))
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
