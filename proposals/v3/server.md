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
- Caching/handling for user-defined and system-generated primary transaction IDs on write
- Add support for websockets
- Change default plugin path
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

#### Transaction Caching
v3 enables [batch writes](writes.md#group-writes) with the [tag](tags.md) based routing
system. As part of this, the notion of *write transaction* changes such that there is a
single *primary transaction* for a write via the Synse API. Each primary transaction
is composed of one or more *component transactions*, which represent a single device write.

The component transaction is the internal transaction state generated by the plugin and
cached in Synse Server. This effectively does not change from v2. 

The primary transaction is an additional layer of abstraction on top of component transaction(s)
which allows:
- component transaction grouping (e.g. batch writes)
- user-defined transaction IDs (e.g. if application is managing transaction on its own)

Just as in v2, the plugin will track the component transactions and will make that data
available to Synse Server for caching. If Synse Server terminates, a new instance can
rebuild the cache from the plugins. If a plugin fails, the data is lost.

In v3, the primary transaction info will only live in Synse Server. All transactions have
a TTL in the system, so they are never persisted. If Synse Server terminates, the
primary transaction information will be lost. 

Synse Server will **not** provide any means for transaction persistence, at least for the
initial release of Synse v3. It is up to the caller to handle cases where a query for
a transaction ID returns in a "not found" error.

See the API doc for more details on [write](api.md#write) and [transaction](api.md#transaction)
behavior.

### Websocket Support
In addition to the HTTP API, Synse Server can expose a [WebSocket](https://tools.ietf.org/html/rfc6455)
API which provides a different usage pattern, giving more flexibility to client needs.

While these updates would need to be reflected in any [API clients](api-clients.md), the
change here is relatively straightforward since [websocket support is build into the Sanic
framework](https://sanic.readthedocs.io/en/latest/sanic/websocket.html). Adding this support
will require updates to how the server is initialized, but should generally be low-impact.

The HTTP API and WebSocket API can coexist and be served simultaneously, which will be the
default behavior. Both the WebSocket and HTTP API can be disabled via config, but at least
one must be enabled for Synse to run. If both are disabled, Synse Server will terminate in
error.

```yaml
transport:
  http: true
  websocket: true
```

### Plugin Activity
To provide better insight into Synse Server's operation with its plugins, a notion of
"plugin activity" is introduced. Simply put, an "active" plugin is one that has successfully
registered with Synse Server and has not failed to communicate with Synse Server in a
number of previous requests.

Plugin activity is surfaced to the user via the [`/plugin`](api.md#plugins) endpoint.

If a plugin is configured but fails to register, it will be considered inactive.

If a plugin stops working and stops responding to Synse, it will be marked as inactive.
Commands are still routed to inactive plugins. The inactive designation is purely for
the API consumer; it does not alter the command dispatching logic in Synse.

If an inactive plugin registers or starts responding again, it will be marked active.

Plugin health is only computed on active plugins. The [`/plugin/health`](api.md#plugin-health)
endpoint provides information on number of active vs. inactive plugins for the consumer
to use, should they wish to include that as a health condition.

### Default Plugin Socket Path
Early in v2 development, the default plugin socket path was chosen to be `/tmp/synse/procs`.

Semantically, `procs` fell out of the old idea that plugins would be "background processes".
To simplify and remove this incorrect semantic, the default path for plugin sockets will
change to `/tmp/synse`.

```
/tmp
  /synse
    emulator.sock
    i2c.sock
    plugin3.sock
```

### FQDN Devices
To support fully-qualified domain names for devices, Synse needs to expose each device via
a unique URL via its API.

The [`/device/{device_id}`](api.md#device) endpoint provides read and write access to a
single device via a unique URL. This together with the deterministic device GUIDs means
that as long as the plugin is up, we can always have read/write access to the same device
from the same URL.

See also: [Amendment 1: Device FQDN & Aliases](amendment-1.md)

### Logging
Logging in Synse Server is not terrible, but it is inconsistent between different regions
of the code. Some areas have many log messages that are verbose, while others lack meaningful
logging.

In addition, the log levels of logs messages should be adjusted to the appropriate severity.

We will also want to add structured logging, particularly around reads, writes, and transactions.
This will be useful for tracing calls across multiple contains/VMs/machines. A potential
solution for structured logging is: https://github.com/hynek/structlog

### Python 3.7
Bumping Python to 3.7 will bring some improved performance. Support for Python 3.6 will not
be dropped.

### Configuration
This section contains an example of a complete configuration for Synse Server in v3. This
includes the various new configuration options proposed in these documents.

```yaml
logging: info
pretty_json: true
locale: en_US
cache:
  device:
    ttl: 20
  transaction:
    ttl: 300
grpc:
  timeout: 3
  tls:
    cert: /tmp/ssl/synse.crt
metrics:  ## New in v3
  enabled: false
transport:  ## New in v3
  http: true
  websocket: true
plugin:
  tcp:
  - emulator-plugin:5001
  unix:
  - /tmp/synse/plugin/foo.sock
  discover:
    kubernetes:
      namespace: vapor
      endpoints:
        labels:
          app: synse
          component: server
```