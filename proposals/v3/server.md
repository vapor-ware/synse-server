# Synse Server
## Summary
Synse Server requires a number of changes based on the switch to a [tag based routing system](tags.md).
In addition to those changes, there are some Synse Server-specific changes
to improve usability and performance.

## High Level Work Items
- Updates required by the new tag based routing system:
  - Updates to API (see: [API](api.md))
  - Updates to internal caching mechanisms
  - Updates to GRPC API
- Simplify internal caching
- Add support for websockets
- Improve logging
- Update to python3.7 for performance improvements (maintain support for 3.6)

## Proposal
### API
Updates to Synse Server regarding updates to the API are not discussed here. Instead
see the [API](api.md) document.

### Pre-processing Behavior
The changes specified in the API document make it clear that the "alias" routes
will be phased out in v3. Most data pre-processing was being done in those endpoints,
but some other endpoints also have pre-processing checks to various degrees.

Synse v3 aims to minimize the amount of pre-processing Synse Server does on the
incoming values (e.g. query params, write data) choosing instead to defer that processing
to the plugin. This allows for more generic device support and puts the onus on the
user to know what a device supports, rather than have the API enforce devices capabilities
(which are not guaranteed across all devices of a given type).

### Caching
In Synse v2, device routing (`rack/board/device`) is accomplished by asking each plugin
for the devices it is managing and subsequently caching this information. This cache is
periodically invalidated and rebuilt to ensure a relatively up-to-date account of all
present devices. Since it is unlikely for devices to be changing frequently, the cache
has a fairly long TTL. 

The device info returned from the plugin includes all of the plugin metadata. In v2,
this included the location (`rack/board/device`). In v3, the rack, board, and device routing
info are being removed in favor of a [tag](tags.md) based system.

Ultimately, the process for building/rebuilding the cache will generally stay the same.
What will change is the structure of the cache, and how cache entries are organized.

In v2, there are multiple caches being built and maintained:

| Name | Description |
| ---- | ----------- |
| *transaction* | Caches recent write transactions with long TTL. |
| *devices* | Caches all devices metainfo from all connected plugins. |
| *plugins* | Cache that tracks which devices belong to which plugin. |
| *scan* | Cache built from the *devices*, formatted for a scan response. |
| *info* | Cache built from the *device*, formatted for an info response. |
| *capabilities* | Cache of the `capabilities` grpc route, for all plugins. |


The number of caches seen above is somewhat excessive and duplicative, but was either
required or convenient for the old device routing solution. The change to the underlying
routing system means that the number of caches will be reduced.

For example, we should no longer need the *scan* cache -- with the tag-based system,
there is no routing hierarchy, so the devices in the scan response do not need special
organization/formatting (see the [Scan API](api.md#scan) changes for details). 

> **TODO**: Discussion on transactions and the best way to handle them, especially
> w.r.t. front-end consumers, e.g. do we want transaction IDs to be global through
> the whole system, or should there be a set of backend transaction IDs mapped to
> frontend transaction IDs?

A lot of the info between caches, e.g. the *devices*, *plugin*, and *info* caches,
could probably also be consolidated into a single model.

Currently (v2), running Synse Server with an external emulator plugin configured over TCP,
we get the approximately the following stats with a light request workload against
Synse Server:

```
CONTAINER ID        NAME                CPU %               MEM USAGE / LIMIT     MEM %               NET I/O             BLOCK I/O           PIDS
7f9ea447c7ef        synse-server        0.28%               50.92MiB / 1.952GiB   2.55%               518kB / 795kB       13.9MB / 0B         11
``` 

While not terrible, this is only with a simple plugin and only a handful of devices.
For comparison, the `docker stats` results for Synse Server when it first starts up,
before it registers and caches any plugins/devices, we see something like:

```
CONTAINER ID        NAME                CPU %               MEM USAGE / LIMIT     MEM %               NET I/O             BLOCK I/O           PIDS
0008048166ff        synse-server        0.04%               48.28MiB / 1.952GiB   2.42%               788B / 0B           0B / 0B             7
```

Which is approximately a 2.64MiB difference in mem usage, the vast majority of which is
from the in-memory caching of the aforementioned device info. At the time of this writing,
the emulator provides 12 devices, so approximately 220kB of cached data is being kept per
device. This will add up as potentially hundreds of devices are added to the system.

### Websocket Support
As an alternative to the current method of interfacing with Synse Server (HTTP), support can
be added to configure it to use [websockets](https://tools.ietf.org/html/rfc6455). This can be
useful for different deployment scenarios.

While these updates would need to be reflected in any [API clients](api-clients.md), the
change here is relatively straightforward since [websocket support is build into the Sanic
framework](https://sanic.readthedocs.io/en/latest/sanic/websocket.html). Adding this support
will require updates to how the server is initialized, but should generally be low-impact.

The transport option will default to HTTP for backwards compatibility. It can be set via
a configuration option.

```yaml
transport: 
  protocol: websocket
```

### Logging
Logging in Synse Server is not terrible, but it is inconsistent between different regions
of the code. Some areas have many log messages that are verbose, while others lack meaningful
logging.

In addition, the log levels of logs messages should be adjusted to the appropriate severity.

### Python 3.7
Bumping Python to 3.7 will bring some improved performance. Support for Python 3.6 will not
be dropped.