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
This section contains the proposed HTTP API specification for Synse v3.

In Synse v1 and v2, the URI was prefixed with `/synse/{version}`. This is a historical
artifact and is no longer needed. To simplify, `v3` will remove the `synse` prefix, so
versioned requests are prefixed with only the API version, e.g. `/v3`.

> Synse also exposes a [WebSocket API](api-websocket.md).

### Errors
Most errors returned from Synse Server will come back with a JSON payload in order to
provide additional context for the error. Some errors will not return a JSON payload;
this class of error is generally due to the service not being ready, available, or
reachable.

#### HTTP Codes
An error response will be returned with one of the following HTTP codes:

* **400**: Invalid user input. This can range from invalid POSTed JSON, unsupported query
  parameters being used, or invalid resource types.
* **404**: The specified resource was not found.
* **405**: Action not supported for device (read/write).
* **500**: Server side processing error.

#### Scheme
Below is an example of an error's JSON response:

```json
{
  "http_code": 404,
  "description": "Device not found",
  "timestamp": "2018-01-24 19:22:28Z",
  "context": "f52d29fecf05a195af13f14c73065252d does not correspond with a known device ID"
}
```

| Field | Description |
| :---- | :---------- |
| *http_code* | The HTTP code corresponding to the error (e.g. 400, 404, 500 -- see [http codes](#http-codes)). |
| *description* | A short description of the error. |
| *timestamp* | The RFC3339 formatted timestamp at which the error occurred. |
| *context* | Contextual message associated with the error to provide root cause info. This will typically include the pertinent internal state. |


### API Endpoints
Below is a table of contents for the API Endpoints.

0. [Metrics](#metrics)
0. [Test](#test)
0. [Version](#version)
0. [Config](#config)
0. [Plugins](#plugins)
0. [Plugin Health](#plugin-health)
0. [Scan](#scan)
0. [Tags](#tags)
0. [Info](#info)
0. [Read](#read)
0. [Read Device](#read-device)
0. [Read Cache](#read-cache)
0. [Write (Asynchronous)](#write-asynchronous)
0. [Write (Synchronous)](#write-synchronous)
0. [Transaction](#transaction)
0. [Device](#device)


---

### Metrics
```
GET http://HOST:5000/metrics
```

An endpoint to get application-based [metrics](monitoring.md#synse-server) for Synse Server.

---

### Test
```
GET http://HOST:5000/test
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
  "timestamp": "2018-11-09T14:32:47Z"
}
``` 

**Fields**

| Field | Description |
| :---- | :---------- |
| *status* | "ok" if the endpoint returns successfully. |
| *timestamp* | The time at which the status was tested. |

##### Error (500)
No JSON - route not reachable/service not ready

* **500** - Catchall processing error


---

### Version
```
GET http://HOST:5000/version
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
| :---- | :---------- |
| *version* | The full version (major.minor.micro) of the Synse Server instance. |
| *api_version* | The API version (major.minor) that can be used to construct subsequent API requests. |

##### Error
No JSON - route not reachable/service not ready

* **500** - Catchall processing error


---

### Config
```
GET http://HOST:5000/v3/config
```

Get a the unified configuration of the Synse Server instance.

This endpoint is added as a convenience to make it easier to determine
what configuration Synse Server is running with. The Synse Server
configuration is made up of default, file, environment, and override
configuration components. This endpoint provides the final joined
configuration that Synse Server ultimately runs with.

#### Response

##### OK (200)
The response JSON will match the configuration scheme. See: [Config](server.md#configuration).

##### Error
See: [Errors](#errors)

* **500** - Catchall processing error


---

### Plugins
```
GET http://HOST:5000/v3/plugin[/{plugin_id}]
```

Get info on the plugins currently registered with Synse Server.

If no URI parameters are supplied, a summary of all plugins is returned. See below
for an example response.

If a plugin has registered with Synse Server and is communicating successfully,
it will be marked as "active". If registration or communication fail, it will be
marked as "inactive".

> *Note*: There is no guarantee that all plugins are represented in the plugins list
> if Synse is configured to use plugin discovery. When discovering plugins, it will
> only register them as the plugins make themselves available.
>
> If all plugins are registered directly via Synse Server configuration, the plugins
> list should always contain all configured plugins.

#### URI Parameters

| Parameter | Required | Description |
| :-------- | :------- | :---------- |
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
    "maintainer": "vapor io",
    "active": true
  },
  {
    "description": "a custom third party plugin",
    "id": "12835beffd3e6c603aa4dd92127707b6",
    "name": "custom-plugin",
    "maintainer": "third-party",
    "active": true
  }
]
```

Below is an example response when the `id` URI parameter is provided.
```json
{
  "active": true,
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
    "timestamp": "2018-06-15T20:04:33Z",
    "status": "ok",
    "message": "",
    "checks": [
      {
        "name": "read buffer health",
        "status": "ok",
        "message": "",
        "timestamp": "2018-06-15T20:04:06Z",
        "type": "periodic"
      },
      {
        "name": "write buffer health",
        "status": "ok",
        "message": "",
        "timestamp": "2018-06-15T20:04:06Z",
        "type": "periodic"
      }
    ]
  }
}
```

**Fields**

| Field | Description |
| :---- | :---------- |
| *active* | This field specifies whether the plugin is active or not. For more see [plugin activity](server.md#plugin-activity) |
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
| :---- | :---------- |
| *name* | The name of the health check. |
| *status* | The status of the health check (ok, failing) |
| *message* | A message describing the failure, if in a failing state. |
| *timestamp* | The timestamp for which the status applies. |
| *type* | The type of health check (e.g. periodic) |

##### Error
See: [Errors](#errors)

* **500** - Catchall processing error
* **404** - Plugin not found


---

### Plugin Health
```
GET http://HOST:5000/v3/plugin/health
```

Get a summary of the health of registered plugins.

This endpoint provides an easy way to programmatically determine whether the plugins
registered with Synse Server are considered healthy by Synse Server. This can also be
done by iterating through the values returned by the `/plugin` endpoint; this endpoint
just makes that information easier and faster to access.

*See also: [Health](health.md)*

#### Response

##### OK (200)
```json
{
  "status": "healthy",
  "updated": "2018-06-15T20:04:33Z",
  "healthy": [
    "12835beffd3e6c603aa4dd92127707b5",
    "12835beffd3e6c603aa4dd92127707b6",
    "12835beffd3e6c603aa4dd92127707b7"
  ],
  "unhealthy": [],
  "active": 3,
  "inactive": 0
}
```

**Fields**

| Field | Description |
| :---- | :---------- |
| *status* | A string describing the overall health state of the registered plugins. This can be either `"healthy"` or `"unhealthy"`. It will only be healthy if *all* plugins are found to be healthy, otherwise the overall state is unhealthy. |
| *updated* | An RFC3339 timestamp describing the time that the plugin health state was last updated. |
| *healthy* | A list containing the plugin IDs for those plugins deemed to be healthy. |
| *unhealthy* | A list containing the plugin IDs for those plugins deemed to be unhealthy. |
| *active* | The count of active plugins. (see: [plugin activity](server.md#plugin-activity)) |
| *inactive* | The count of inactive plugins. (see: [plugin activity](server.md#plugin-activity)) |

##### Error
See: [Errors](#errors)

* **500** - Catchall processing error


---

### Scan
```
GET http://HOST:5000/v3/scan
```

List the devices that Synse knows about and can read from/write to via
the configured plugins.

This endpoint provides an aggregated view of the devices made known to Synse
Server by each of the registered plugins. This endpoint provides a high-level
view of what exists in the system. Scan info can be filtered to show only those
devices which match a set of provided tags.

By default, scan results are sorted by device id. The `sort` query parameter
can be used to modify the sort behavior.

#### Query Parameters

| Key  | Description |
| :--- | :---------- |
| ns | The default namespace to use for the specified labels. (default: `default`) |
| tags | The [tags](tags.md) to filter devices on. If specifying multiple tags, they should be comma-separated. |
| force | Force a re-scan (do not use the cache). This will take longer than scanning using the cache, since it needs to rebuild the cache. (default: false) |
| sort | Specify the fields to sort by. Multiple fields can be specified as a comma separated string, e.g. `"plugin,id"`. The "tags" field can not be used for sorting. (default: "plugin,sort_index,id", where the `sort_index` is an internal sort preference which a plugin can optionally specify.) |

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

**Fields**

| Field | Description |
| :---- | :---------- |
| *id* | The globally unique ID for the device. |
| *info* | A human readable string providing identifying info about a device. |
| *type* | The type of the device, as defined by its plugin. |
| *plugin* | The ID of the plugin which the device is managed by. |
| *tags* | A list of the tags associated with this device. One of the tags will be the `id` tag. |

##### Error
See: [Errors](#errors)

* **500** - Catchall processing error
* **400** - Invalid parameter(s)


---

### Tags
```
GET http://HOST:5000/v3/tags
```

List all of the tags currently associated with devices.

This will list the tags in the specified tag namespace. If no tag namespace
is specified (via query parameters), the default tag namespace is used.

By default, this endpoint will omit the `id` tags since they match the
device id enumerated by the [`/scan`](#scan) endpoint. The `id` tags can
be included in the response by setting the `ids` query parameter to `true`.

Multiple tag namespaces can be queried at once by using a comma delimiter
between namespaces in the `ns` query parameter value string, e.g.
`?ns=default,ns1,ns2`.

Tags are sorted alphanumerically.

#### Query Parameters

| Key  | Description |
| :--- | :---------- |
| ns | The tag namespace(s) to use when searching for tags. (default: `default`) |
| ids | A flag which determines whether `id` tags are included in the response. (default: `false`) |

#### Response

##### OK (200)
```json
[
  "default/tag1",
  "default/type:temperature"
]
```

##### Error
See: [Errors](#errors)

* **500** - Catchall processing error
* **400** - Invalid parameter(s)


---

### Info
```
GET http://HOST:5000/v3/info/{device_id}
```

Get the full set of metainfo and capabilities for a specified device.


#### URI Parameters

| Parameter | Required | Description |
| :-------- | :------- | :---------- |
| *device_id* | yes | The ID of the device to get info for. IDs should be globally unique. |

#### Response

##### OK (200)
```json
{
  "timestamp": "2018-06-18T13:30:15Z",
  "id": "34c226b1afadaae5f172a4e1763fd1a6",
  "type": "humidity",
  "metadata": {
    "model": "emul8-humidity"
  },
  "plugin": "12835beffd3e6c603aa4dd92127707b5",
  "info": "Synse Humidity Sensor",
  "tags": [
      "type:humidity",
      "humidity",
      "vio/fan-sensor"
  ],
  "capabilities": {
    "mode": "rw",
    "read": {},
    "write": {
      "actions": [
        "color", 
        "state"
      ]
    }
  },
  "output": [
    {
      "name": "humidity",
      "type": "humidity",
      "precision": 3,
      "scaling_factor": 1.0,
      "units": [
        {
          "system": null,
          "name": "percent humidity",
          "symbol": "%"
        }
      ]
    },
    {
      "name": "temperature",
      "type": "temperature",
      "precision": 3,
      "scaling_factor": 1.0,
      "units": [
        {
          "system": "metric",
          "name": "celsius",
          "symbol": "C"
        },
        {
          "system": "imperial",
          "name": "fahrenheit",
          "symbol": "F"
        }
      ]
    }
  ]
}
```

**Fields**

| Field | Description |
| :---- | :---------- |
| *timestamp* | An RFC3339 timestamp describing the time that the device info was gathered. |
| *id* | The globally unique ID for the device. |
| *type* | The device type, as specified by the plugin. |
| *metadata* | A map of arbitrary values that provide additional data for the device. |
| *plugin* | The ID of the plugin that manages the device. |
| *info* | A human readable string providing identifying info about a device. |
| *tags* | A list of the tags associated with this device. One of the tags will be the 'id' tag which should match the `id` field. |
| *capabilities* | Specifies the actions which the device is able to perform (e.g. read, write). See below for more. |
| *output* | A list of the output types that the device supports. |


**Capabilities Fields**

| Field | Description |
| :---- | :---------- |
| *mode* | A string specifying the device capabilities. This can be "r" (read only), "rw" (read write), "w" (write only). |
| *read* | Any additional information regarding the device reads. This will currently remain empty. |
| *write* | Any additional information regarding device writes. |
| *write.actions* | A list of actions which the device supports for writing. |


**Output Fields**

| Field | Description |
| :---- | :---------- |
| *name* | The name of the output type. This can be namespaced. |
| *type* | The type of the output, as defined by the plugin. |
| *precision* | The number of decimal places the value will be rounded to. |
| *scaling_factor* | A scaling factor which will be applied to the raw reading value. |
| *units* | Information for the reading's units of measure. |
| *unit.system* | The system of measure that the unit belongs to. |
| *unit.name* | The complete name of the unit of measure (e.g. "meters per second"). |
| *unit.symbol* | A symbolic representation of the unit of measure (e.g. m/s). |

##### Error
See: [Errors](#errors)

* **500** - Catchall processing error
* **404** - Device not found


---

### Read
```
GET http://HOST:5000/v3/read
```

Read data from devices which match the set of provided tags. 

Passing in the `id` tag here is functionally equivalent to using the [read device](#read-device)
endpoint.

Reading data will be returned for devices which match *all* of the specified tags.
The contents of prior reads is not necessarily indicative of the content of future
reads. That is to say, if a plugin terminates and a read command is issued, the
devices managed by that plugin which would have matched the tags are no longer available
to Synse (until the plugin comes back up), and as such, can not be read from.
When the plugin becomes available again, the devices from that plugin are available
to be read from.

For readability, readings are sorted by a combination of originating plugin, any
plugin-specified sort index on the reading's device, and by device id.

For more details on the changes to the `/read` endpoint, see the 
[Synse Reads Document](./reads.md)

#### Query Parameters

| Key  | Description |
| :--- | :---------- |
| ns | The default namespace to use for the specified labels. (default: `default`) |
| tags | The [tags](tags.md) to filter devices on. If specifying multiple tags, they should be comma-separated. |
| som | The System of Measure for the response reading(s). This should be one of: imperial, metric. (default: `metric`) |

#### Response
It is recommended to read the document on [v3 reads](reads.md), as it explains in detail
the changes to the read response.

##### OK (200)
> **Note**: In the examples below, the key-value pairs in the `context` field
> are arbitrary and only serve as an example of possible values.

```json
[
  {
    "device": "a72cs6519ee675b",
    "device_type": "temperature",
    "type": "temperature",
    "value": 20.3,
    "timestamp": "2018-02-01T13:47:40Z",
    "unit": {
      "system": "metric",
      "symbol": "C",
      "name": "degrees celsius"
    },
    "context": {
      "host": "127.0.0.1",
      "sample_rate": 8
    }
  },
  {
    "device": "929b923de65a811",
    "device_type": "led",
    "type": "state",
    "value": "off",
    "timestamp": "2018-02-01T13:47:40Z",
    "unit": null
  },
  {
    "device": "929b923de65a811",
    "device_type": "led",
    "type": "color",
    "value": "000000",
    "timestamp": "2018-02-01T13:47:40Z",
    "unit": null
  },
  {
    "device": "12bb12c1f86a86e",
    "device_type": "door_lock",
    "type": "status",
    "value": "locked",
    "timestamp": "2018-02-01T13:47:40Z",
    "unit": null,
    "context": {
      "wedge": 1,
      "zone": "6B"
    }
  }
]
```

The `context` field of a reading is optional and allows the plugin to specify additional
context for the reading. This can be useful in modeling the data for various kinds of
plugins/read behavior.

As an example, a plugin could provide additional data for a reading such as which host
the data originated from, a sample rate, etc (for something like sFlow). Since the context
can contain arbitrary data, it can also be used to label particular readings making them
easier to parse upstream. An example of this would be associating multiple lock devices
with their physical location.

**Fields**

| Field | Description |
| :---- | :---------- |
| *device* | The ID of the device which the reading originated from. |
| *device_type* | The type of the device. |
| *type* | The type of the reading. |
| *value* | The value of the reading. |
| *timestamp* | An RFC3339 timestamp describing the time at which the reading was taken. |
| *unit* | The unit of measure for the reading. If there is no unit, this will be `null`. |
| *context* | A mapping of arbitrary values to provide additional context for the reading. |

##### Error
See: [Errors](#errors)

* **500** - Catchall processing error
* **400** - Invalid parameter(s)


---

### Read Device
```
GET http://HOST:5000/v3/read/{device_id}
```

Read from the specified device. This endpoint is effectively the same as using the [`/read`](#read)
endpoint where the label matches the [device id tag](tags.md#auto-generated), e.g.
`http://HOST:5000/v3/read?tags=id:b33f7ac0`.

#### URI Parameters

| Parameter | Required | Description |
| :-------- | :------- | :---------- |
| *device_id* | yes | The ID of the device to read. [Device IDs](ids.md) are globally unique. |

#### Query Parameters

| Key  | Description |
| :--- | :---------- |
| som | The System of Measure for the response reading(s). This should be one of: imperial, metric. (default: `metric`) |

#### Response

##### OK (200)
The response schema for the `/read/{device_id}` endpoint is the same as the response schema
for the [`/read`](#read) endpoint.

> **Note**: In the examples below, the key-value pairs in the `context` field
> are arbitrary and only serve as an example of possible values.

```json
[
  {
    "device": "12bb12c1f86a86e",
    "device_type": "temperature",
    "type": "temperature",
    "value": 20.3,
    "timestamp": "2018-02-01T13:47:40Z",
    "unit": {
      "system": "metric",
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

**Fields**

| Field | Description |
| :---- | :---------- |
| *device* | The ID of the device which the reading originated from. |
| *device_type* | The type of the device. |
| *type* | The type of the reading. |
| *value* | The value of the reading. |
| *timestamp* | An RFC3339 timestamp describing the time at which the reading was taken. |
| *unit* | The unit of measure for the reading. If there is no unit, this will be `null`. |
| *context* | A mapping of arbitrary values to provide additional context for the reading. |

##### Error
See: [Errors](#errors)

* **500** - Catchall processing error
* **404** - Device not found


---

### Read Cache
```
GET http://HOST:5000/v3/readcache
```

Stream reading data from the registered plugins.

All plugins have the capability of caching their readings locally in order to maintain
a higher resolution of state beyond the poll frequency which Synse Server may request at.
This is particularly useful for push-based plugins, where we would lose the pushed
reading if it were not cached.

At the plugin level, caching read data can be enabled, but is disabled by default. Even if
disabled, this route will still return data for every device that supports reading on each
of the configured plugins. When read caching is disabled, this will just return a dump of
the current state for all readings which is maintained by the plugin.

#### Query Parameters

| Key  | Description |
| :--- | :---------- |
| start | An RFC3339 formatted timestamp which specifies a starting bound on the cache data to return. If no timestamp is specified, there will not be a starting bound. |
| end | An RFC3339 formatted timestamp which specifies an ending bound on the cache data to return. If no timestamp is specified, there will not be an ending bound. |

#### Response

##### OK (200)
The response schema for the `/readcache` endpoint is the same as the response schema
for the [`/read`](#read) endpoint.

Unlike the [`/read`](#read) and [`/read/{device_id}`](#read-device) endpoints, the response for this endpoint is
streamed JSON. One block of the streamed JSON will appear as follows:

> **Note**: In the examples below, the key-value pairs in the `context` field
> are arbitrary and only serve as an example of possible values.

```json
[
  {
    "device": "a72cs6519ee675b",
    "device_type": "temperature",
    "type": "temperature",
    "value": 20.3,
    "timestamp": "2018-02-01T13:47:40Z",
    "unit": {
      "system": "metric",
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

**Fields**

| Field | Description |
| :---- | :---------- |
| *device* | The ID of the device which the reading originated from. |
| *device_type* | The type of the device. |
| *type* | The type of the reading. |
| *value* | The value of the reading. |
| *timestamp* | An RFC3339 timestamp describing the time at which the reading was taken. |
| *unit* | The unit of measure for the reading. If there is no unit, this will be `null`. |
| *context* | A mapping of arbitrary values to provide additional context for the reading. |


##### Error
See: [Errors](#errors)

* **500** - Catchall processing error
* **400** - Invalid query parameters


---

### Write (Asynchronous)
```
POST http://HOST:5000/v3/write/{device_id}
```

Write data to a device, in an asynchronous manner.

This endpoint allows writes to be issued to Synse Server, where they will be processed
asynchronously and their status can be polled at some later time. An alternative is to
use the [synchronous write](#write-synchronous) endpoint.

This endpoint will return a transaction ID associated with each write. For simplicity
and to reduce partial state failure cases, Synse only supports writing to a single device
per request, however multiple values can be written to the device if desired. When specifying
multiple write operations for a device, they are processed in the order which they are
provided in the POSTed JSON body.

Not all devices support writing. The write capabilities of a device are defined at the plugin
level and are exposed via the [`/info`](#info) endpoint. If a write is issued to a device which
does not support writing, an error is returned.

For more details on the changes to the `/write` endpoint, see the 
[Synse Writes Document](./writes.md)

#### URI Parameters

| Parameter | Required | Description |
| :-------- | :------- | :---------- |
| *device_id* | yes | The ID of the device that is being written to. |

#### POST Body
```json
[
  {
    "transaction": "56a32eba-1aa6-4868-84ee-fe01af8b2e6d",
    "action": "color",
    "data": "f38ac2"
  }
]
```

**Fields**

| Field | Required | Description |
| :---- | :------- | :---------- |
| *transaction* | no | A user-defined transaction ID for the write. If this conflicts with an existing transaction ID, an error is returned. If this is not specified, a transaction ID will be automatically generated for the write action. |
| *action* | yes | The action that the device will perform. This is set at the plugin level and exposed in the [`/info`](#info) endpoint. |
| *data* | sometimes | Any data that an action may require. Not all actions require data. This is plugin-defined. |


To batch multiple writes to a device, the additional writes can be appended to the
POST body JSON list. The writes will be processed in the order which they are provided
in this list. In the example below, "color" will be processed first, then "state".

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

#### Response

##### OK (200)
```json
[
  {
    "context": {
      "action": "color",
      "data": "f38ac2"
    },
    "device": "0fe8f06229aa9a01ef6032d1ddaf18a2",
    "transaction": "56a32eba-1aa6-4868-84ee-fe01af8b2e6d",
    "timeout": "10s"
  },
  {
    "context": {
      "action": "state",
      "data": "blink"
    },
    "device": "0fe8f06229aa9a01ef6032d1ddaf18a2",
    "transaction": "56a32eba-1aa6-4868-84ee-fe01af8b2e6e",
    "timeout": "10s"
  }
]
```

**Fields**

| Field | Description |
| :---- | :---------- |
| *context* | The data written to the device. This is provided as context info to help identify the write action. |
| *device* | The GUID of the device being written to. |
| *transaction* | The ID for the device write transaction. This can be passed to the [`/transaction`](#transaction) endpoint to get the status of the write action. |
| *timeout* | The timeout for the write transaction, after which it will be cancelled. This is effectively the maximum wait time for the transaction to resolve. This is defined by the plugin. |

##### Error
See: [Errors](#errors)

* **500** - Catchall processing error
* **400** - Invalid JSON provided
* **404** - Device not found
* **405** - Device does not support writing


---

### Write (Synchronous)
```
POST http://HOST:5000/v3/write/wait/{device_id}
```

Write data to a device, waiting for the write to complete.

This endpoint is the synchronous version of the [asynchronous write](#write-asynchronous) endpoint.
In some cases, it may be more convenient to just wait for a response instead of continually
polling Synse Server to check whether the transaction completed. For these cases, this endpoint
can be used.

Note that the length of time it takes for a write to complete depends on the device and its
plugin, so there is likely to be a variance in response times when waiting. It is up to the
user to define a sane timeout such that the request does not prematurely terminate.

#### URI Parameters

| Parameter | Required | Description |
| :-------- | :------- | :---------- |
| *device_id* | yes | The ID of the device that is being written to. |

#### POST Body
```json
[
  {
    "transaction": "56a32eba-1aa6-4868-84ee-fe01af8b2e6d",
    "action": "color",
    "data": "f38ac2"
  }
]
```

**Fields**

| Field | Required | Description |
| :---- | :------- | :---------- |
| *device* | yes | The ID of the device being written to. |
| *transaction* | no | A user-defined transaction ID for the write. If this conflicts with an existing transaction ID, an error is returned. If this is not specified, a transaction ID will be automatically generated for the write action. |
| *action* | yes | The action that the device will perform. This is set at the plugin level and exposed in the [`/info`](#info) endpoint. |
| *data* | sometimes | Any data that an action may require. Not all actions require data. This is plugin-defined. |


To batch multiple writes to a device, the additional writes can be appended to the
POST body JSON list. The writes will be processed in the order which they are provided
in this list. In the example below, "color" will be processed first, then "state".

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

#### Response

##### OK (200)
```json
[
 {
   "id": "56a32eba-1aa6-4868-84ee-fe01af8b2e6d",
   "timeout": "10s",
   "device": "0fe8f06229aa9a01ef6032d1ddaf18a5",
   "context": {
     "action": "color",
     "data": "f38ac2"
   },
   "status": "done",
   "created": "2018-02-01T15:00:51Z",
   "updated": "2018-02-01T15:00:51Z",
   "message": ""
 }
]
```

The response for a synchronous write has the same scheme as the [`/transaction`](#transaction) response,
albeit in a list. Some of these fields will not matter to the caller of the synchronous write endpoint,
such as the transaction `id`. 

It is up to the user to iterate though the response and ensure that each individual write completed
successfully. While this endpoint will fail in cases where the plugin is not reachable, the data is
invalid, etc., it will not fail if a write fails to execute properly.

##### Error
See: [Errors](#errors)

* **500** - Catchall processing error
* **400** - Invalid JSON provided
* **404** - Device not found
* **405** - Device does not support writing


---

### Transaction
```
GET http://HOST:5000/v3/transaction[/{transaction_id}]
```

Check the state and status of a write transaction.

If no *transaction_id* is given, a sorted list of all cached transaction IDs is returned. The
length of time that a transaction is cached is configurable (see the Synse Server [configuration](server.md#configuration)).

If the provided transaction ID does not exist, an error is returned.

#### URI Parameters

| Parameter | Required | Description |
| :-------- | :------- | :---------- |
| *transaction_id* | no | The ID of the write transaction to get the status of. Transaction IDs are provided from an [asynchronous write](#write-asynchronous) response. |


#### Response

##### OK (200)
```json
{
  "id": "56a32eba-1aa6-4868-84ee-fe01af8b2e6b",
  "timeout": "10s",
  "device": "0fe8f06229aa9a01ef6032d1ddaf18a5",
  "context": {
    "action": "color",
    "data": "f38ac2"
  },
  "status": "done",
  "created": "2018-02-01T15:00:51Z",
  "updated": "2018-02-01T15:00:51Z",
  "message": ""
}
```

**Fields**

| Field | Description |
| :---- | :---------- |
| *id* | The ID of the transaction. This is generated and assigned by the plugin being written to. |
| *timeout* | A string representing the timeout for the write transaction after which it will be cancelled. This is effectively the maximum wait time for the transaction to resolve. |
| *device* | The GUID of the device being written to. |
| *context* | The POSTed write data for the given write transaction. |
| *status* | The current status of the transaction. (`pending`, `writing`, `done`, `error`) |
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

##### Error
See: [Errors](#errors)

* **500** - Catchall processing error
* **404** - Transaction not found

#### Status
Transaction can have one of four statuses:

| Status | Description |
| :----- | :---------- |
| *pending* | The write was received and queued but has not yet been processed. |
| *writing* | The write has been taken off the queue and is being processed. |
| *done* | The write has been processed and completed successfully. (terminal state) |
| *error* | The write failed for any reason. (terminal state) |


---

### Device
```
GET  http://HOST:5000/v3/device/{device_id}
POST http://HOST:5000/v3/device/{device_id}
```

Read and write to a device.

This endpoint allows read and write access to a device through a single URL,
allowing for FQDN devices. A device can be read via `GET` and written to via `POST`.
The underlying implementations for read and write are the same as the [`/read/{device}`](#read-device)
and [`/write/wait/{device}`](#write-synchronous) requests, respectively.

#### URI Parameters

| Parameter | Required | Description |
| :-------- | :------- | :---------- |
| *device_id* | yes | The ID of the device that is being read from/written to. |

#### POST Body
```json
[
  {
    "transaction": "56a32eba-1aa6-4868-84ee-fe01af8b2e6d",
    "action": "color",
    "data": "f38ac2"
  }
]
```

**Fields**

| Field | Required | Description |
| :---- | :------- | :---------- |
| *device* | yes | The ID of the device being written to. |
| *transaction* | no | A user-defined transaction ID for the write. If this conflicts with an existing transaction ID, an error is returned. If this is not specified, a transaction ID will be automatically generated for the write action. |
| *action* | yes | The action that the device will perform. This is set at the plugin level and exposed in the [`/info`](#info) endpoint. |
| *data* | sometimes | Any data that an action may require. Not all actions require data. This is plugin-defined. |


#### Response

##### OK (200)
**`GET`**
(See: [`/read`](#read-device))

> **Note**: In the examples below, the key-value pairs in the `context` field
> are arbitrary and only serve as an example of possible values.

```json
[
  {
    "device": "12bb12c1f86a86e",
    "device_type": "temperature",
    "type": "temperature",
    "value": 20.3,
    "timestamp": "2018-02-01T13:47:40Z",
    "unit": {
      "system": "metric",
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



**`POST`**
(See: [`/write`](#write-synchronous))

```json
[
 {
   "id": "56a32eba-1aa6-4868-84ee-fe01af8b2e6d",
   "timeout": "10s",
   "device": "0fe8f06229aa9a01ef6032d1ddaf18a5",
   "context": {
     "action": "color",
     "data": "f38ac2"
   },
   "status": "done",
   "created": "2018-02-01T15:00:51Z",
   "updated": "2018-02-01T15:00:51Z",
   "message": ""
 }
]
```

##### Error
See: [Errors](#errors)

* **500** - Catchall processing error
* **400** - Invalid JSON provided/Invalid parameters
* **404** - Device not found
* **405** - Device does not support reading/writing
