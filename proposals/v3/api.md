# Synse v3 HTTP API
## Summary
The driving change for Synse v3 is removing `rack/board/device`-based routing
and using a new [tag](tags.md)-based routing system. This change is reflected in
the API by replacing the old routing components with the new ones. In addition,
various API improvements are included. These improvements are both a result of the
new routing system and a result of feedback from v2 API usage.

## High Level Work Items
- Update the HTTP API in accordance with the API spec detailed in this document
- Look into using [swagger](https://swagger.io/) for API documentation generation

## Proposal
This section contains the proposed API specification for Synse v3.

Following the pattern established in previous versions of Synse Server,
the URI prefix for requests will be `/synse/{API_VERSION}`, except for the two
unversioned endpoints (`/test` and `/version`) where the URI prefix is just
`/synse`.

> **Highlights of Major Changes**:
>  - `/scan` response change: removes device hierarchy, returns flattened list of devices
>  - `/read` behavior change: no longer uses hierarchical routing, uses tags
>  - `/write` behavior change: no longer uses hierarchical routing, uses tags
>  - removes alias routes - behavior similar to alias routes can now be done via vanilla `/read` and `/write`

> We could keep the alias routes around, but looking forward, it doesn't seem scalable since we could
> have tens or hundreds of different device types supported by the system. In addition, not all of the
> "LED" type devices may support the same thing, e.g., so it doesn't make sense to handle all LEDs the
> same way. We could make a more generic means of checking inputs per device, not just per device type,
> so it wouldn't matter how many device types there are and how they vary -- they could be checked automatically
> and the API wouldn't need to be updated/modified for each of them.

> Do we want to support more ways to access the API? Just HTTP? Add external gRPC api? websockets?
> We probably don't need this configurability right now, but it could be worth considering or looking
> in to, particularly if we start measuring system performance and need to improve it.

### Errors
Most errors returned from Synse Server will come back with a JSON payload in order to
provide additional context for the error. Some errors will not return a JSON payload;
this class of error is generally due to the service not being ready, available, or
reachable.

#### Codes
An error response will be returned with one of the following HTTP codes:

* **400**: Invalid user input. This can range from invalid POSTed JSON, unsupported query
  parameters being used, or invalid resource types.
* **404**: Invalid URL or the specified resource is not found.
* **500**: Server-side processing error.

> **Question**: Should we support more error codes (finer grained)? In the past we've tried to use
> as few codes as we can get away with to keep things simple. Does it make sense to return more
> fine-grained error codes, or do these "high level" buckets suffice?

#### Scheme
Below is an example of an error's JSON response:

```json
{
  "http_code": 404,
  "error_id": 4000,
  "description": "device not found",
  "timestamp": "2018-01-24 19:22:28.425090",
  "context": "f52d29fecf05a195af13f14c73065252d does not correspond with a known device ID"
}
```

| Field | Description |
| ----- | ----------- |
| *http_code* | The HTTP code corresponding to the error (e.g. 400, 404, 500 -- see [codes](#codes). |
| *error_id* | The [internal ID](#error-ids) for the error. This can be used to further identify the error origin. |
| *description* | A short description of the error. This is the human-readable version of the `error_id`. |
| *timestamp* | The RFC3339Nano-formatted timestamp at which the error occurred. |
| *context* | Additional contextual message associated with the error to provide root cause info. This will typically include the pertinent internal state. |


#### Error IDs
Below is a table defining the internal `error_id`, along with their corresponding
human-readable description.

| Error ID | Deprecated | Description |
| -------- | ---------- | ----------- |
| 0 | no | Unknown |
| **3xxx**: Request error |
| 3000 | no | URL not found |
| 3001 | no | Invalid arguments |
| 3002 | no | Invalid JSON |
| 3003 | yes (in v3) | Invalid device type |
| **4xxx errors**: Not found |
| 4000 | no | Device not found |
| 4001 | yes (in v3) | Board not found |
| 4002 | yes (in v3) | Rack not found |
| 4003 | no | Plugin not found |
| 4004 | no | Transaction not found |
| **5xxx errors**: Failed command |
| 5000 | no | Failed *info* command |
| 5001 | no | Failed *read* command |
| 5002 | no | Failed *scan* command |
| 5003 | no | Failed *transaction* command |
| 5004 | no | Failed *write* command |
| 5005 | no | Failed *plugin* command |
| 5006 | no | Failed *read cached* command |
| **6xxx errors**: Plugin errors |
| 6000 | no | Internal API failure (GRPC) |
| 6500 | no | Plugin state error |



### API Endpoints
Below is a table of contents for the API Endpoints.

0. [Test](#test)
0. [Version](#version)
0. [Config](#config)
0. [Plugins](#plugins)
0. [Plugin Health](#plugin-health)
0. [Scan](#scan)
0. [Health](#health)
0. [Capabilities](#capabilities)
0. [Read](#read)
0. [Read Device](#read-device)
0. [Read Cached](#read-cached)
0. [Write](#write)
0. [Transaction](#transaction)


---

### Test
> No changes from v2

```
GET http://HOST:5000/synse/test
```

A dependency and side-effect free check to see whether Synse Server is
reachable and responsive.

If the endpoint is reachable (e.g. if Synse Server is up and ready), this
will return a 200 response with the described JSON response. If the test
endpoint is unreachable or otherwise fails, it will return a 500 response.
The test endpoint does not have any internal dependencies, so a failure would
indicate Synse Server not being up and serving.

#### Response

##### OK (200)
```json
{
  "status": "ok",
  "timestamp": "2018-11-09T14:32:47.354313Z"
}
``` 

**Fields**

| Field | Description |
| ----- | ----------- |
| *status* | "ok" if the endpoint returns successfully. |
| *timestamp* | The time at which the status was tested. |

##### Error (500)
No JSON - route not reachable/service not ready


---

### Version
> No changes from v2

```
GET http://HOST:5000/synse/version
```

Get the version info of the Synse Server instance. The API version
provided by this endpoint should be used in subsequent requests.

#### Response

##### OK (200)
```json
{
  "version": "3.0.0",
  "api_version": "v3"
}
```

**Fields**

| Field | Description |
| ----- | ----------- |
| *version* | The full version (major.minor.micro) of the Synse Server instance. |
| *api_version* | The API version (major.minor) that can be used to construct subsequent API requests. |

##### Error (500)
No JSON - route not reachable/service not ready


---

### Config
```
GET http://HOST:5000/synse/config
```

Get a the unified configuration of the Synse Server instance.

This endpoint is added as a convenience to make it easier to determine
what configuration Synse Server is running with. The Synse Server
configuration is made up of default, file, environment, and override
configuration components. This endpoint provides the final joined
configuration that Synse Server ultimately runs with.

#### Response

##### OK (200)
The response JSON will match the configuration scheme.

##### Error (500)
See: [Errors](#errors)


---

### Plugins
> **Changed**: Added an `id` field to the response.

```
GET http://HOST:5000/synse/v3/plugin[/{plugin_id}]
```

Get info on the plugins currently registered with Synse Server.

If no URI parameters are supplied, a summary of all plugins is returned. See below
for an example response.

#### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| *id* | no | The ID of the plugin to get more information for. Plugin IDs can be enumerated via the `/plugin` endpoint without specifying a URI parameter. |

#### Response

##### OK (200)

Below is an example response when no query parameters are provided. This will
result in a summary of all registered plugins.
```json
[
  {
    "description": "a plugin with emulated devices and data",
    "id": "12835beffd3e6c603aa4dd92127707b5",
    "name": "emulator plugin",
    "maintainer": "vapor io"
  },
  {
    "description": "a custom third party plugin",
    "id": "12835beffd3e6c603aa4dd92127707b6",
    "name": "custom-plugin",
    "maintainer": "third-party"
  }
]
```

Below is an example response when the `id` URI parameter is provided.
```json
{
  "id": "12835beffd3e6c603aa4dd92127707b5",
  "tag": "vaporio\/emulator-plugin",
  "name": "emulator plugin",
  "description": "A plugin with emulated devices and data",
  "maintainer": "vaporio",
  "vcs": "github.com\/vapor-ware\/synse-emulator-plugin",
  "version": {
    "plugin_version": "2.0.0",
    "sdk_version": "1.0.0",
    "build_date": "2018-06-14T16:24:09",
    "git_commit": "13e6478",
    "git_tag": "1.0.2-5-g13e6478",
    "arch": "amd64",
    "os": "linux"
  },
  "network": {
    "protocol": "tcp",
    "address": "emulator-plugin:5001"
  },
  "health": {
    "timestamp": "2018-06-15T20:04:33.4393472Z",
    "status": "ok",
    "message": "",
    "checks": [
      {
        "name": "read buffer health",
        "status": "ok",
        "message": "",
        "timestamp": "2018-06-15T20:04:06.3524458Z",
        "type": "periodic"
      },
      {
        "name": "write buffer health",
        "status": "ok",
        "message": "",
        "timestamp": "2018-06-15T20:04:06.3523946Z",
        "type": "periodic"
      }
    ]
  }
}
```

**Fields**

| Field | Description |
| ----- | ----------- |
| *id* | An id hash for identifying the plugin, generated from plugin metadata. |
| *tag* | The plugin tag. This is a normalized string made up of its name and maintainer. |
| *name* | The name of plugin. |
| *maintainer* | The maintainer of the plugin. |
| *description* | A short description of the plugin. |
| *vcs* | A link to the version control repo for the plugin. |
| *version* | An object that contains version information about the plugin. |
| *version.plugin_version* | The plugin version. |
| *version.sdk_version* | The version of the Synse SDK that the plugin is using. |
| *version.build_date* | The date that the plugin was built. |
| *version.git_commit* | The git commit at which the plugin was built. |
| *version.git_tag* | The git tag at which the plugin was built. |
| *version.arch* | The architecture that the plugin is running on. |
| *version.os* | The OS that the plugin is running on. |
| *network* | An object that describes the network configurations for the plugin. |
| *network.protocol* | The protocol that is used to communicate with the plugin (unix, tcp). |
| *network.address* | The address of the plugin for the protocol used. |
| *health* | An object that describes the overall health of the plugin. |
| *health.timestamp* | The time at which the health status applies. |
| *health.status* | The health status of the plugin (ok, degraded, failing, error, unknown) |
| *health.message* | A message describing the error, if in an error state. |
| *health.checks* | A collection of health check snapshots for the plugin. |


There may be 0..N health checks for a Plugin, depending on how it is configured.
The health check elements here make up a snapshot of the plugin's health at a given time.

| Field | Description |
| ----- | ----------- |
| *name* | The name of the health check. |
| *status* | The status of the health check (ok, failing) |
| *message* | A message describing the failure, if in a failing state. |
| *timestamp* | The timestamp for which the status applies. |
| *type* | The type of health check (e.g. periodic) |

##### Error (500)
See: [Errors](#errors)


---

### Plugin Health
```
GET http://HOST:5000/synse/v3/plugins/health
```

Get a summary of the health of registered plugins.

This endpoint provides an easy way to programmatically determine whether the plugins
registered with Synse Server are considered healthy by Synse Server. This can also be
done by iterating through the values returned by the `/plugins` endpoint; this endpoint
just makes that information easier and faster to access.

*See also: [Health](health.md)*

#### Response

##### OK (200)
```json
{
  "status": "healthy",
  "updated": "2018-06-15T20:04:33.4393472Z",
  "healthy": [
    "12835beffd3e6c603aa4dd92127707b5",
    "12835beffd3e6c603aa4dd92127707b6",
    "12835beffd3e6c603aa4dd92127707b7"
  ],
  "unhealthy": []
}
```

**Fields**

| Field | Description |
| ----- | ----------- |
| *status* | A string describing the overall health state of the registered plugins. This can be either `"healthy"` or `"unhealthy"`. It will only be healthy if *all* plugins are found to be healthy, otherwise the overall state is unhealthy. |
| *updated* | An RFC3339 timestamp describing the time that the plugin health state was last updated. |
| *healthy* | A list containing the plugin IDs for those plugins deemed to be healthy. |
| *unhealthy* | A list containing the plugin IDs for those plugins deemed to be unhealthy. |

##### Error (500)
See: [Errors](#errors)

---

### Scan
```
GET http://HOST:5000/synse/v3/scan
```

List the devices that Synse knows about and can read from/write to via
the configured plugins.

This endpoint provides an aggregated view of the devices made known to Synse
Server by each of the registered plugins. This endpoint provides a high-level
view of what exists in the system. Scan info can be filtered to show only those
devices which match a set of provided tags.

The scan results are sorted by device id.

#### Query Parameters

| Key | Description |
| --- | ----------- |
| ns | The default namespace to use for the specified labels. (default: `default`) |
| tags | The [tags](tags.md) to filter devices on. If specifying multiple tags, they should be comma-separated. |
| force | Force a re-scan (do not use the cache). This will take longer than scanning using the cache, since it needs to rebuild the cache. (default: false) |
| sort | Specify the fields to sort by. Multiple fields can be specified as a comma separated string, e.g. `"plugin,id"`. (default: "id") |

#### Response

##### OK (200)
```json
[
  {
    "id": "0fe8f06229aa9a01ef6032d1ddaf18a5",
    "info": "Synse Temperature Sensor",
    "type": "temperature",
    "plugin": "12835beffd3e6c603aa4dd92127707b5",
    "tags": [
      "type:temperature",
      "temperature",
      "vio/fan-sensor"
    ]
  },
  {
    "id": "12ea5644d052c6bf1bca3c9864fd8a44",
    "info": "Synse LED",
    "type": "led",
    "plugin": "12835beffd3e6c603aa4dd92127707b5",
    "tags": [
      "type:led",
      "led"
    ]
  }
]
```

##### Error (500, 400)
See: [Errors](#errors)


---

### Health
```
GET http://HOST:5000/synse/v3/health
```

*See also: [Health](health.md)*

#### Response

##### OK (200)

##### Error (500)
See: [Errors](#errors)


---

### Capabilities?
> Not sure this endpoint is needed, but can't hurt to have...

```
GET http://HOST:5000/synse/v3/capabilities
```

#### Response

##### OK (200)

##### Error (500)
See: [Errors](#errors)


---

### Info
> **Changes**: There is no longer a need for a distinction between rack/board/device
> info -- its all just device info now.

```
GET http://HOST:5000/synse/v3/info/{device_id}
```

Get the full set of metainfo for a specified device.

> **Question**: Should we include additional information here, e.g. whether the device
> supports reading/writing, what actions/data it will accept for writes, etc. This seems
> like it would be good to expose *somewhere* in the API, but it is unclear whether we
> should include it here in the device info, or somewhere else (like device capabilities?)

#### URI Parameters

| Parameter | Description |
| --------- | ----------- |
| *device_id* | The ID of the device to get info for. IDs should be globally unique. |

#### Response

##### OK (200)
```json
{
  "timestamp": "2018-06-18T13:30:15.6554449Z",
  "uid": "34c226b1afadaae5f172a4e1763fd1a6",
  "kind": "humidity",
  "metadata": {
    "model": "emul8-humidity"
  },
  "plugin": "emulator plugin",
  "info": "Synse Humidity Sensor",
  "tags": [
      "type:humidity",
      "humidity",
      "vio/fan-sensor"
  ],
  "capabilities": {
    "read": true,
    "write": false,
  },
  "output": [
    {
      "name": "humidity",
      "type": "humidity",
      "precision": 3,
      "scaling_factor": 1.0,
      "unit": {
        "name": "percent humidity",
        "symbol": "%"
      }
    },
    {
      "name": "temperature",
      "type": "temperature",
      "precision": 3,
      "scaling_factor": 1.0,
      "unit": {
        "name": "celsius",
        "symbol": "C"
      }
    }
  ]
}
```

##### Error (500, 404)
See: [Errors](#errors)


---

### Read
```
GET http://HOST:5000/synse/v3/read
```

For more details on the changes to the `/read` endpoint, see the 
[Synse Reads Document](./reads.md)


> As part of the response scheme, we want to add an optional "context" or "metadata"
> field. This field should hold a dict that can contain arbitrary values.

Having some optional context associated with a reading (or group of readings) would make
it easier to model certain types of data, and would ultimately make the data more usable
upstream. An example of this would be that a plugin could provide additional metadata
for a reading (e.g. which host the data came from, a sampling rate, etc). Upstream, this
metadata could be converted into prometheus labels for the reading.

> **Open Question**:
> For the 'context' field, described above, do we want it at an individual reading
> level, at the level of the entire reading response, or for it to be possible at
> both (e.g. ctx for this reading value in particular vs. ctx that applies to all
> the readings)


#### Query Parameters

| Key | Description |
| --- | ----------- |
| ns | The default namespace to use for the specified labels. (default: `default`) |
| tags | The [tags](tags.md) to filter devices on. If specifying multiple tags, they should be comma-separated. |

#### Response
It is recommended to read the document on [v3 reads](reads.md), as it explains in detail
the changes to the read response.

##### OK (200)
```json
{
  "a72cs6519ee675b": [
    {
      "kind": "temperature",
      "type": "temperature",
      "value": 20.3,
      "timestamp": "2018-02-01T13:47:40.395939895Z",
      "info": "",
      "unit": {
        "symbol": "C",
        "name": "degrees celsius"
      },
      "context": {
        "host": "127.0.0.1",
        "sample_rate": 8
      }
    }
  ],
  "929b923de65a811": [
    {
      "kind": "led",
      "type": "state",
      "value": "off",
      "timestamp": "2018-02-01T13:47:40.395939895Z",
      "info": "",
      "unit": null
    },
    {
      "kind": "led",
      "type": "color",
      "value": "000000",
      "timestamp": "2018-02-01T13:47:40.395939895Z",
      "info": "",
      "unit": null
    }
  ],
  "12bb12c1f86a86e": [
    {
      "kind": "door_lock",
      "type": "lock",
      "value": "locked",
      "timestamp": "2018-02-01T13:47:40.395939895Z",
      "info": "Zone 6B",
      "unit": null,
      "context": {
        "wedge": 1
      }
    }
  ]
}
```

##### Error (500, 400)
See: [Errors](#errors)


---

### Read Device
```
GET http://HOST:5000/synse/v3/read/{device_id}
```

Read from the specified device. This endpoint is effectively the same as using the [`/read`](#read)
endpoint where the label matches the [device id tag](tags.md#auto-generated), e.g.
`http://HOST:5000/synse/v3/read?tags=id:b33f7ac0`.

#### URI Parameters

| Parameter | Description |
| --------- | ----------- |
| *device_id* | The ID of the device to read. IDs should be globally unique. |


#### Response

##### OK (200)
The response here is similar to the response for the `/read` endpoint, except it just returns
the list of readings for the device, instead of a collection of 1 `device_id` keyed to this
device reading info. 

> **Question**: We have a bunch of different response formats for reads - "read", "read device", 
> and "read cached". They all convey the same data, just structured a bit differently to make it
> convenient for each of their use cases (bulk read, single read, streamed read -- respectively).
> Would it make sense to try and unify the response data structures into a more uniform response
> or just accept that since the endpoints are catered towards different use cases, the format of
> the data they return will vary?

```json
[
  {
    "kind": "temperature",
    "type": "temperature",
    "value": 20.3,
    "timestamp": "2018-02-01T13:47:40.395939895Z",
    "info": "",
    "unit": {
      "symbol": "C",
      "name": "degrees celsius"
    },
    "context": {
      "host": "127.0.0.1",
      "sample_rate": 8
    }
  }
]
```

##### Error (500, 404)
See: [Errors](#errors)


---

### Read Cached
```
GET http://HOST:5000/synse/v3/readcached
```

Stream reading data from the registered plugins.

All plugins have the capability of caching their readings locally in order to maintain
a higher resolution of state beyond the poll frequency which Synse Server may request at.
This is particularly useful for push-based plugins, where we would lose the pushed
reading if it were not cached.

At the plugin level, caching read data can be enabled, but is disabled by default. Even if
disabled, this route will still return data for every device that supports reading on each
of the configured plugins. When read caching is disabled, this will just return a dump of
the "current" reading state that is maintained by the plugin.

#### Query Parameters

| Key | Description |
| --- | ----------- |
| start | An RFC3339 or RFC3339Nano formatted timestamp which specifies a starting bound on the cache data to return. If no timestamp is specified, there will not be a starting bound. |
| end | An RFC3339 or RFC3339Nano formatted timestamp which specifies an ending bound on the cache data to return. If no timestamp is specified, there will not be an ending bound. |

#### Response

##### OK (200)
The response will be streamed JSON. One block of the streamed JSON will appear as follows:
```json
{
  "id": "a72cs6519ee675b",
  "data": [
    {
      "kind": "temperature",
      "type": "temperature",
      "value": 20.3,
      "timestamp": "2018-02-01T13:47:40.395939895Z",
      "info": "",
      "unit": {
        "symbol": "C",
        "name": "degrees celsius"
      },
      "context": {
        "host": "127.0.0.1",
        "sample_rate": 8
      }
    }
  ]
}
```

This is similar to the [read](#read) response, but organized a bit differently to make it
more suitable for streaming.

##### Error (500, 400)
See: [Errors](#errors)


---

### Write
```
POST http://HOST:5000/synse/v3/write
```

Write data to devices.

The write endpoint supports both single device writes and bulk device writes. This
is mediated through the [tag](tags.md) based routing system.
- To write to a single device, the unique `id` tag for the target device should be used.
- To write to multiple devices, any number of non-`id` tags can be used.

If writing to multiple devices, each device write will be resolved asynchronously. Each
device write will have its own internal transaction. This means that even if some of the
devices matching the specified tags fail (either from a precondition check or actual write
failure), all other device writes will not be cancelled or blocked.

Separate from multi-device writes are multi-value writes, where a single write command
can write multiple values to a device. Each value to be written is passed as an action/data
pair within the POST body. Writes are evaluated in order of their position in the list, e.g.
for the following POST body, the color value would be written first, then the state value.

```json
[
  {
    "action": "color",
    "data": "f38ac2"
  },
  {
    "action": "state",
    "data": "blink"
  }
]
```

For more details on the changes to the `/write` endpoint, see the 
[Synse Writes Document](./writes.md)

#### POST Body
Example for a single-value write:
```json
[
  {
    "action": "color",
    "data": "f38ac2"
  }
]
```

Example for a multi-value write:
```json
[
  {
    "action": "color",
    "data": "f38ac2"
  },
  {
    "action": "state",
    "data": "blink"
  }
]
```

#### Query Parameters

| Key | Required | Description |
| --- | -------- | ----------- |
| ns | no | The default namespace to use for the specified labels. (default: `default`) |
| tags | yes | The [tags](tags.md) to filter devices on. If specifying multiple tags, they should be comma-separated. |
| transaction | no | A user-defined transaction ID which will be used as the primary write transaction id. If this conflicts with an existing transaction ID, an error is returned. |

See [Writes](writes.md) for more info on writing to devices using tags.

#### Response

##### OK (200)
The write response consists of a "primary write transaction id" (e.g. `56a32eba-1aa6-4868-84ee-fe01af8b2e6d`, below)
and a collection of individual device writes. The primary transaction id is used to identify the API
write action as a whole, while the individual device writes each represent a write to a device. In cases
where a single device is written to, there will only be one device write under the *"writes"* field.
In cases where multiple devices are written to, there will be multiple device writes.

```json
{
  "transaction": "56a32eba-1aa6-4868-84ee-fe01af8b2e6d",
  "writes": [
    {
      "context": [
        {
          "action": "color",
          "data": "f38ac2"
        }
      ],
      "device": "0fe8f06229aa9a01ef6032d1ddaf18a2",
      "transaction": "b9keavu8n63001v6bnm0"
    }
  ]
}
```

For multiple device writes:
```json
{
  "transaction": "56a32eba-1aa6-4868-84ee-fe01af8b2e6b",
  "writes": [
    {
      "context": [
        {
          "action": "color",
          "data": "f38ac2"
        }
      ],
      "device": "0fe8f06229aa9a01ef6032d1ddaf18a3",
      "transaction": "b9keavu8n63001v6bnm1"
    },
    {
      "context": [
        {
          "action": "color",
          "data": "f38ac2"
        }
      ],
      "device": "0fe8f06229aa9a01ef6032d1ddaf18a4",
      "transaction": "b9keavu8n63001v6bnm2"
    },
    {
      "context": [
        {
          "action": "color",
          "data": "f38ac2"
        }
      ],
      "device": "0fe8f06229aa9a01ef6032d1ddaf18a5",
      "transaction": "b9keavu8n63001v6bnm3"
    }
  ]
}
```

**Fields**

| Field | Description |
| ----- | ----------- |
| *transaction* | The primary write transaction id. If a user-defined transaction is provided via the `transaction` query parameter, this field will hold that ID. Otherwise, a new ID is generated. |
| *writes* | The collection of individual device writes which make up the write request. |

Each device write object has the following fields:

| Field | Description |
| ----- | ----------- |
| *context* | The data written to the device. This is provided as context info to help identify the action. |
| *device* | The GUID of the device being written to. |
| *transaction* | The internal ID for the device write. |

##### Error (500, 400)
See: [Errors](#errors)


---

### Transaction
```
GET http://HOST:5000/synse/v3/transaction[/{transaction_id}]
```

Check the state and status of a write transaction.

The *transaction_id* parameter can be either the primary write transaction id, or the id of an
individual device write. 

When a primary write transaction id is provided, the return state and status are an aggregate of
all component device writes, where both state and status contain the "least complete" value from
their component device writes. That is to say, if a write contained two device writes, one of which
was complete and the other was pending, the overall state and status returned would be that of the
pending device write. If *any* component write fails, the primary write will resolve to an error
state/status.

When a component device write transaction id is provided, the return state will be that of the
device write.

If no transaction ID is given, a list of all cached primary transaction IDs, sorted by
transaction ID (the `id` response field), is returned. The length of time that a transaction
is cached is configurable (see the Synse Server [configuration documentation]()).

If the provided transaction ID does not exist, an error is returned.

#### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| *transaction_id* | no | The ID of the write transaction to get the status of. Transaction IDs are provided from a corresponding [write](#write) response. |


#### Response

##### OK (200)
Below is an example of the 200 OK response from the `/transaction` endpoint when a primary transaction ID
is provided:

```json
{
  "id": "56a32eba-1aa6-4868-84ee-fe01af8b2e6b",
  "state": "ok",
  "status": "done",
  "message": "",
  "components": [
    "b9pin8ofmg5g01vmt77g"
  ]
}
```

**Fields**

| Field | Description |
| ----- | ----------- |
| *id* | The primary ID of the transaction. |
| *state* | The "least complete" state of the component transactions. (`ok`, `error`) |
| *status* | The "least complete" status of the component transactions. (`unknown`, `pending`, `writing`, `done`) |
| *message* | Any context information relating to a transaction's error state. If there is no error, this will be an empty string. |
| *components* | The ID(s) for the component device write transaction(s). |

Below is an example of the 200 OK response from the `/transaction` endpoint when a component device write transaction ID
is provided:
```json
{
  "id": "b9pin8ofmg5g01vmt77g",
  "device": "0fe8f06229aa9a01ef6032d1ddaf18a5",
  "context": {
    "action": "color",
    "data": "f38ac2"
  },
  "state": "ok",
  "status": "done",
  "created": "2018-02-01T15:00:51.132823149Z",
  "updated": "2018-02-01T15:00:51.132823149Z",
  "message": ""
}
```

**Fields**

| Field | Description |
| ----- | ----------- |
| *id* | The ID of the transaction. This is generated and assigned by the plugin being written to. |
| *device* | The GUID of the device being written to. |
| *context* | The POSTed write data for the given write transaction. |
| *state* | The current state of the transaction. (`ok`, `error`) |
| *status* | The current status of the transaction. (`unknown`, `pending`, `writing`, `done`) |
| *created* | The time at which the transaction was created. This timestamp is generated by the plugin. |
| *updated* | The last time the transaction state *or* status was updated. Once the transaction reaches a `done` status or `error` state, no further updates will occur. |
| *message* | Any context information relating to a transaction's error state. If there is no error, this will be an empty string. |


Below is an example of the 200 OK response from the `/transaction` endpoint when no transaction ID
is provided:

```json
[
  "56a32eba-1aa6-4868-84ee-fe01af8b2e6b",
  "56a32eba-1aa6-4868-84ee-fe01af8b2e6c",
  "56a32eba-1aa6-4868-84ee-fe01af8b2e6d"
]
```

##### Error (500, 404)
See: [Errors](#errors)

#### States
Transactions can be in one of two states:

| State | Description |
| ----- | ----------- |
| *ok* | The default state. This signifies that the transaction is being processed regularly and has encountered no errors. |
| *error* | The error state. This signifies an error with handling or resolving the transaction at any point during its lifecycle. |

#### Status
Transaction can have one of four statuses:

| Status | Description |
| ------ | ----------- |
| *unknown* | The transaction is unknown - this is likely due to it not being found. |
| *pending* | The write is queued but has not yet been processed. |
| *writing* | The write has been taken off the queue and is being processed. |
| *done* | The write has been processed and is complete. |