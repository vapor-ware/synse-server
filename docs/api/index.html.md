---
title: API Reference

language_tabs:
  - shell
  - python

toc_footers:
  - Vapor IO • Synse Server • v2.0.0

search: true
---

# Overview

Synse Server provides a simple JSON API to monitor and control physical and virtual devices, such as
data center and IT equipment. More generally, it provides a uniform interface for back-ends implementing
various protocols, such as RS485 and I2C. The Synse Server API makes it easy to read from and write
to devices, gather device information, and scan for configured devices through a curl-able interface.


# Errors

```json
{
  "http_code": 404,
  "error_id": 4000,
  "description": "device not found",
  "timestamp": "2018-01-24 19:54:37.382551",
  "context": "rack-1\/board-1\/f52d29fecf05a195af13f14c73065252d does not correspond with a known device."
}
```

Synse Server will return a JSON response with 400, 404, or 500 code errors. The returned JSON is used
to provide context around the error. An example of the response JSON for an error is shown here.

In general,

- **400 responses** relate to invalid user input. This can range from invalid JSON, unsupported
  query parameters, or invalid resource types.
- **404 responses** relate to either the specified URL not being valid or the specified
  resource was not found.
- **500 responses** relate to server-side processing errors.

The fields for the error response are:

| Field | Description |
| ----- | ----------- |
| *http_code* | The HTTP code corresponding to the the error (e.g. 400, 404, 500). |
| *error_id* | The Synse Server defined error ID. This is used to identify the type of error. |
| *description* | A short description for the error type, as defined by the `error_id`. |
| *timestamp* | The time at which the error occurred. |
| *context* | Any message associated with the error to provide information on the root cause of the error. |


The currently defined error IDs follow.

| Error ID | Description |
| -------- | ----------- |
| 0 | Unknown Error |
| 3000 | URL not found |
| 3001 | Invalid arguments |
| 3002 | Invalid JSON |
| 3003 | Invalid device type |
| 4000 | Device not found |
| 4001 | Board not found |
| 4002 | Rack not found |
| 4003 | Plugin not found |
| 4004 | Transaction not found |
| 5000 | Failed info command |
| 5001 | Failed read command |
| 5002 | Failed scan command |
| 5003 | Failed transaction command |
| 5004 | Failed write command |
| 6000 | Internal API failure |
| 6500 | Plugin state error |


# Device Types
Devices in Synse Server are all associated with "type" information (For the full set of information
associated with a device, see the [info](#info) endpoint). While the device types are defined by the
plugin which manages the device, common device types in Synse include:

- airflow
- fan
- humidity
- led
- pressure
- temperature


# Endpoints

## Test

```shell
curl "http://host:5000/synse/test"
```

```python
import requests

response = requests.get('http://host:5000/synse/test')
```

> The response JSON would be structured as:

```json
{
  "status": "ok",
  "timestamp": "2018-01-24 19:22:28.425090"
}
```

Test that the endpoint is reachable.

If the endpoint is reachable (e.g. if Synse Server is up and ready), this will return a 200 response
with the described JSON response. If the test endpoint is unreachable or otherwise fails, it will return
a 500 response. The test endpoint does not have any internal dependencies, so a failure would indicate
Synse Server not being up and serving.

<aside class="notice">
    Note that a 500 response from this endpoint would likely <b>not</b> include any JSON context,
    as a 500 here generally means Synse Server is either not yet running or otherwise unreachable.
</aside>

### HTTP Request

`GET http://host:5000/synse/test`

### Response Fields

| Field | Description |
| ----- | ----------- |
| *status* | "ok" if the endpoint returns successfully. |
| *timestamp* | The time at which the status was tested. |



## Version

```shell
curl "http://host:5000/synse/version"
```

```python
import requests

response = requests.get('http://host:5000/synse/version')
```

> The response JSON would be structured as:

```json
{
  "version": "2.0.0",
  "api_version": "2.0"
}

```

Get the version info of the Synse Server instance. The API version provided by this endpoint
should be used in subsequent requests.

### HTTP Request

`GET http://host:5000/synse/version`

### Response Fields

| Field | Description |
| ----- | ----------- |
| *version* | The full version (major.minor.micro) of the Synse Server instance. |
| *api_version* | The API version (major.minor) that can be used to construct subsequent API requests. |



## Config

```shell
curl "http://host:5000/synse/2.0/config"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/config')
```

> The response JSON would be structured as:

```json
{
  "logging": "debug",
  "pretty_json": true,
  "locale": "en_US",
  "plugin": {
    "unix": {
      "emulator": null
    }
  },
  "cache": {
    "meta": {
      "ttl": 20
    },
    "transaction": {
      "ttl": 300
    }
  },
  "grpc": {
    "timeout": 3
  }
}
```

Get the unified configuration of the Synse Server instance.

This endpoint is added as a convenience to make it easier to determine what configuration Synse Server
is running with. The Synse Server configuration is made up of default, file, environment, and override
configuration components. This endpoint provides the final joined configuration that Synse Server
ultimately runs with.

See the [Configuration Documentation](http://synse-server.readthedocs.io/en/latest/user/configuration.html)
for more information.

### HTTP Request

`GET http://host:5000/synse/2.0/config`

### Response

The response to the `config` endpoint is the unified configuration for Synse Server. The
[Configuration Documentation](http://synse-server.readthedocs.io/en/latest/user/configuration.html)
describes the configuration scheme in more detail.



## Plugins

```shell
curl "http://host:5000/synse/2.0/plugins"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/plugins')
```

> The response JSON would be structured as:

```json
[
  {
    "name": "emulator",
    "network": "unix",
    "address": "\/tmp\/synse\/procs\/emulator.sock"
  }
]
```

Get all the plugins that are currently registered with Synse Server. 

This endpoint is added as a convenience to make it easier to determine which plugins Synse Server
is running with. Plugins can be registers with Synse Server in a variety of ways, including
file and environment configurations. See the [User Guide](http://synse-server.readthedocs.io/en/latest/index.html)
for more on how to register plugins with Synse Server. This endpoint shows the unified view of all registered plugins.

### HTTP Request

`GET http://host:5000/synse/2.0/plugins`

### Response

| Field | Description |
| ----- | ----------- |
| *name* | The name of plugin. |
| *network* | The plugin's network mode. (unix, tcp)|
| *address* | The address of the plugin. (unix socket path, tcp address) |



## Scan

```shell
curl "http://host:5000/synse/2.0/scan"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/scan')
```

> The response JSON would be structured as:

```json
{
  "racks": [
    {
      "id": "rack-1",
      "boards": [
        {
          "id": "vec",
          "devices": [
            {
              "id": "eb100067acb0c054cf877759db376b03",
              "info": "Synse Temperature Sensor 1",
              "type": "temperature"
            },
            {
              "id": "83cc1efe7e596e4ab6769e0c6e3edf88",
              "info": "Synse Temperature Sensor 2",
              "type": "temperature"
            },
            {
              "id": "329a91c6781ce92370a3c38ba9bf35b2",
              "info": "Synse Temperature Sensor 4",
              "type": "temperature"
            },
            {
              "id": "f97f284037b04badb6bb7aacd9654a4e",
              "info": "Synse Temperature Sensor 5",
              "type": "temperature"
            },
            {
              "id": "eb9a56f95b5bd6d9b51996ccd0f2329c",
              "info": "Synse Fan",
              "type": "fan"
            },
            {
              "id": "f52d29fecf05a195af13f14c7306cfed",
              "info": "Synse LED",
              "type": "led"
            },
            {
              "id": "d29e0bd113a484dc48fd55bd3abad6bb",
              "info": "Synse Backup LED",
              "type": "led"
            }
          ]
        }
      ]
    }
  ]
}
```

Enumerate all known devices that Synse Server can access via its plugins, grouped by rack and board.

The `scan` endpoint provides an aggregated view of the devices, organized by their rack and board
locations, which are made known to Synse Server by each of the registered plugin back-ends. The
`scan` response provides a high-level view of what exists and how to route to it. This routing
information (e.g. rack ID, board ID, device ID) can be used in subsequent commands such as [read](#read),
[write](#write), and [info](#info).

By default, `scan` will enumerate all devices on all boards on all racks. The `rack` and `board` URI
parameters, defined below, can be used to refine the scan to return devices only within the scope of
the given rack or board.

### HTTP Request

`GET http://host:5000/synse/2.0/scan[/{rack}[/{board}]]`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| *rack*    | no       | The id of the rack to scan. *Required only if specifying board.* |
| *board*   | no       | The id of the board to scan. |

### Query Parameters

| Parameter | Default | Description |
| --------- | ------- | ----------- |
| *force*   | false   | Force a re-scan of all known devices. This invalidates the existing cache, causing it to be rebuilt. *Valid values:* `true` |

### Response Fields

| Field | Description |
| ----- | ----------- |
| *racks* | A list of objects which represent a rack. |
| *{rack}.id* | The primary identifier for the rack. |
| *{rack}.boards* | A list of board object which belong to the rack. |
| *{board}.id* | The primary identifier for the board. |
| *{board}.devices* | A list of device objects which belong to the board. |
| *{device}.id* | The primary identifier for the device. |
| *{device}.info* | Any notational information associated with the device to help identify it in a more human-readable way. Note that this is not guaranteed to be unique across devices. |
| *{device}.type* | The [type](#device-types) of the device. |



## Read

```shell
curl "http://host:5000/synse/2.0/read/rack-1/vec/eb100067acb0c054cf877759db376b03"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/read/rack-1/vec/eb100067acb0c054cf877759db376b03')
```

> The response JSON would be structured as:

```json
{
  "type": "temperature",
  "data": {
    "temperature": {
      "value": 20.3,
      "timestamp": "2018-02-01T13:47:40.395939895Z",
      "unit": {
        "symbol": "C",
        "name": "degrees celsius"
      }
    }
  }
}
```

> Devices can provide multiple readings, e.g. an LED device could give a JSON response like:

```json
{
  "type": "led",
  "data": {
    "state": {
      "value": "off",
      "timestamp": "2018-02-01T13:48:59.573898829Z",
      "unit": null
    },
    "color": {
      "value": "000000",
      "timestamp": "2018-02-01T13:48:59.573898829Z",
      "unit": null
    }
  }
}
```

Read data from a known device.

Devices may not necessarily support reading, and the reading values for one device of a given type
may not match those of a different device with the same type. That is to say, the read behavior for
a device is defined at the plugin level, and may differ from plugin to plugin or device to device.

If a read is not supported, an error will be returned with the JSON response specifying the cause
as reads not permitted.

### HTTP Request

`GET http://host:5000/synse/2.0/read/{rack}/{board}/{device}`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| *rack*    | yes      | The id of the rack containing the device to read. |
| *board*   | yes      | The id of the board containing the device to read. |
| *device*  | yes      | The id of the device to read. |

These values can be found via the [scan](#scan) command.

### Response Fields

| Field | Description |
| ----- | ----------- |
| *type*  | The type of the device that was read. See [Device Types](#device-types) for more info. |
| *data*  | An object where the keys specify the *reading type* and the values are the corresponding reading objects. Note that a reading type is not the same as the device type. |
| *{reading}.value* | The value for the given reading type. |
| *{reading}.timestamp* | The time at which the reading was taken. |
| *{reading}.unit* | The unit of measure for the reading. If the reading has no unit, this will be `null`. |
| *{unit}.name* | The long name of the unit. *(e.g. "acceleration")* |
| *{unit}.symbol* | The symbol (or short name) of the unit. *(e.g. "m/s^2")* |


## Write

```shell
curl \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{"action": "color", "raw": "f38ac2"}' \
  "http://host:5000/synse/2.0/write/rack-1/vec/f52d29fecf05a195af13f14c7306cfed"
```

```python
import requests

data = {
    'action': 'color',
    'raw': 'f38ac2'
}

response = requests.post(
    'http://host:5000/synse/2.0/write/rack-1/vec/f52d29fecf05a195af13f14c7306cfed', 
    json=data
)
```

> The response JSON would be structured as:

```json
[
  {
    "context": {
      "action": "color",
      "raw": [
        "f38ac2"
      ]
    },
    "transaction": "b9keavu8n63001v6bnm0"
  }
]
```

Write data to a known device.

Devices may not necessarily support writing, and the write actions for one device of a given type
may not match those of a different device with the same type. That is to say, the write behavior for
a device is defined at the plugin level, and may differ from plugin to plugin or device to device.

If a write is not supported, an error will be returned with the JSON response specifying the cause
as writes not permitted.

The `write` endpoint does not do any data validation upfront, as it is intended to be a generalized
write command. Some "alias" routes exists which allow writing to a specific device type. For those
routes ([led](#led), [fan](#fan)), validation is done on the provided data, to the best extent it
can be.

The data POSTed for a write consists of two peices: an `action`, and `raw` data. The values for these
change based on the device type/plugin, but in general the `action` specifies what will change and
`raw` is the data needed to make that change. See below for more details.

### HTTP Request

`POST http://host:5000/synse/2.0/write/{rack}/{board}/{device}`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| *rack*    | yes      | The id of the rack containing the device to write to. |
| *board*   | yes      | The id of the board containing the device to write to. |
| *device*  | yes      | The id of the device to write to. |

These values can be found via the [scan](#scan) command.

### POST Body

The post body requires an "action" and "raw" to be specified, e.g.

> Example POSTed JSON

```json
{
  "action": "color",
  "raw": "ff0000"
}
```

| Field | Description |
| ----- | ----------- |
| *action* | The write action to perform. This is device-specific. |
| *raw* | The data associated with the given action. |

The valid values and requirements for `action` and `raw` are dependent on the device type/plugin
implementation. For example, an `LED` device supports the actions: `color`, `state`; a
`fan` device supports `speed`. 

Some devices may only need an `action` specified. Some may need both `action` and `raw` specified.
While it is up to the underlying plugin to determine what are valid values for a device, generally,
the `action` should be the attribute to set and `raw` should be the value to set it to.

### Response Fields

| Field | Description |
| ----- | ----------- |
| *context* | The write payload that was POSTed. This is included to help make transactions more identifiable. |
| *transaction* | The ID of the write transaction. Each write will have its own ID. The status of a transaction can be checked with the [transaction](#transaction) command. |



## Transaction

```shell
curl "http://host:5000/synse/2.0/transaction/b9pin8ofmg5g01vmt77g"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/transaction/b9pin8ofmg5g01vmt77g')
```

> The response JSON would be structured as:

```json
{
  "id": "b9pin8ofmg5g01vmt77g",
  "context": {
    "action": "color",
    "raw": [
      "f38ac2"
    ]
  },
  "state": "ok",
  "status": "done",
  "created": "2018-02-01T15:00:51.132823149Z",
  "updated": "2018-02-01T15:00:51.132823149Z",
  "message": ""
}
```

> To list all cached transactions:

```shell
curl "http://host:5000/synse/2.0/transaction"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/transaction')
```

> The response JSON would be structured as:

```json
[
  "b9pin8ofmg5g01vmt77g",
  "baqgsm0if78g01rr9vqg"
]
```


Check the state and status of a write transaction.

If no transaction ID is given, a list of all cached transaction IDs is returned. The length
of time that a transaction is cached for is configurable. See the Synse Server configuration
[Configuration Documentation](http://synse-server.readthedocs.io/en/latest/user/configuration.html)
for more.

### HTTP Request

`GET http://host:5000/synse/2.0/transaction[/{transaction id}]`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| *transaction id* | no | The ID of the write transaction to get the status of. This is given by the corresponding [write](#write). |

### Response Fields

| Field | Description |
| ----- | ----------- |
| *id*      | The ID of the transaction. |
| *context* | The POSTed write data for the given write transaction. |
| *state*   | The current state of the transaction. *Valid values:* (`ok`, `error`) |
| *status*  | The current status of the transaction. *Valid values:* (`unknown`, `pending`, `writing`, `done`)|
| *created* | The time at which the transaction was created (e.g. the write issued). |
| *updated* | The last time the state or status was updated for the transaction. If the transaction has state `ok` and status `done`, no further updates will occur. |
| *message* | Any context information for the transaction relating to its error state. If there is no error, this will be an empty string. |


## Info

> The `info` endpoint will return different responses based on the scope of the request. For 
> a rack-level request:

```shell
curl "http://host:5000/synse/2.0/info/rack-1"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/info/rack-1')
```

> The response JSON would be structured as:

```json
{
  "rack": "rack-1",
  "boards": [
    "vec"
  ]
}
```

> For a board-level request:

```shell
curl "http://host:5000/synse/2.0/info/rack-1/vec"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/info/rack-1/vec')
```

> The response JSON would be structured as:

```json
{
  "board": "vec",
  "location": {
    "rack": "rack-1"
  },
  "devices": [
    "eb9a56f95b5bd6d9b51996ccd0f2329c",
    "f52d29fecf05a195af13f14c7306cfed",
    "d29e0bd113a484dc48fd55bd3abad6bb",
    "eb100067acb0c054cf877759db376b03",
    "83cc1efe7e596e4ab6769e0c6e3edf88",
    "db1e5deb43d9d0af6d80885e74362913",
    "329a91c6781ce92370a3c38ba9bf35b2",
    "f97f284037b04badb6bb7aacd9654a4e"
  ]
}
```

> For a device-level request:

```shell
curl "http://host:5000/synse/2.0/info/rack-1/vec/db1e5deb43d9d0af6d80885e74362913"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/info/rack-1/vec/db1e5deb43d9d0af6d80885e74362913')
```

> The response JSON would be structured as:

```json
{
  "timestamp": "2018-02-01T15:29:31.934013127Z",
  "uid": "db1e5deb43d9d0af6d80885e74362913",
  "type": "temperature",
  "model": "emul8-temp",
  "manufacturer": "Vapor IO",
  "protocol": "emulator",
  "info": "Synse Temperature Sensor 3",
  "comment": "",
  "location": {
    "rack": "rack-1",
    "board": "vec"
  },
  "output": [
    {
      "type": "temperature",
      "data_type": "float",
      "precision": 2,
      "unit": {
        "name": "degrees celsius",
        "symbol": "C"
      },
      "range": {
        "min": 0,
        "max": 100
      }
    }
  ]
}
```

Get the available information for the specified resource.

### HTTP Request

`GET http://host:5000/synse/2.0/info/{rack}[/{board}[/{device}]]`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| *rack*    | yes      | The id of the rack to get info for. |
| *board*   | no       | The id of the board to get info for. *Required only if specifying device.* |
| *device*  | no       | The id of the device to get info for. |

### Response Fields

***Rack Level Response***

| Field | Description |
| ----- | ----------- |
| *rack* | The ID of the rack. |
| *boards* | A list of IDs for boards that belong to the rack. |

***Board Level Response***

| Field | Description |
| ----- | ----------- |
| *board* | The ID of the board. |
| *location* | An object which provides information on its hierarchical parents (e.g. rack). |
| *devices* | A list of IDs for devices that belong to the board. |

***Device Level Response***

| Field | Description |
| ----- | ----------- |
| *timestamp* | The time at which the device info was last retrieved. |
| *uid* | The unique (per board) ID of the device. |
| *type* | The type of the device. (see [Device Types](#device-types) for more.) |
| *model* | The model of the device, as set in the plugin prototype configuration. |
| *manufacturer* | The manufacturer of the device, as set in the plugin prototype configuration. |
| *protocol* | The protocol by which we interface with the device. |
| *info* | Any human-readable information set to help identify the given device. |
| *comment* | Any additional comment set for the given device. |
| *location* | An object which provides information on its hierarchical parents (e.g. rack, board). |
| *output* | The specification for how the device's reading(s) should be output. |



## LED

> If no *valid* query parameters are specified, this will **read** from the LED device.

```shell
curl "http://host:5000/synse/2.0/led/rack-1/vec/f52d29fecf05a195af13f14c7306cfed"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/led/rack-1/vec/f52d29fecf05a195af13f14c7306cfed')
```

> The response JSON will be the same as read response:

```json
{
  "type": "led",
  "data": {
    "state": {
      "value": "off",
      "timestamp": "2018-02-01T16:16:04.884816422Z",
      "unit": null
    },
    "color": {
      "value": "f38ac2",
      "timestamp": "2018-02-01T16:16:04.884816422Z",
      "unit": null
    }
  }
}
```

> If any *valid* query parameters are specified, this will **write** to the LED device.

```shell
curl "http://host:5000/synse/2.0/led/rack-1/vec/f52d29fecf05a195af13f14c7306cfed?color=00ff00&state=on"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/led/rack-1/vec/f52d29fecf05a195af13f14c7306cfed?color=00ff00&state=on')
```

> The response JSON will be the same as a write response:

```json
[
  {
    "context": {
      "action": "state",
      "raw": [
        "on"
      ]
    },
    "transaction": "b9pjujgfmg5g01vmt7b0"
  },
  {
    "context": {
      "action": "color",
      "raw": [
        "00ff00"
      ]
    },
    "transaction": "b9pjujgfmg5g01vmt7bg"
  }
]
```


An alias to `read` from or `write` to a known LED device.

While an LED device can be read directly via the [read](#read) route or written to directly from the
[write](#write) route, this route provides some additional checks and validation before dispatching to
the appropriate plugin handler. In particular, it checks if the specified device is an LED device and
that the given query parameter value(s), if any, are permissible.

If no valid query parameters are specified, this endpoint will read the specified device. If any number
of valid query parameters are specified, the endpoint will write to the specified device.

### HTTP Request

`GET http://host:5000/synse/2.0/led/{rack}/{board}/{device}`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| *rack*    | yes      | The id of the rack containing the LED device to read from/write to. |
| *board*   | yes      | The id of the board containing the LED device to read from/write to. |
| *device*  | yes      | The id of the LED device to read from/write to. |

### Query Parameters

| Parameter | Description |
| --------- | ----------- |
| *state*   | The state of the LED. *Valid values:* (`on`, `off`, `blink`) |
| *color*   | The color of the LED. This must be an RGB hexadecimal color string. |

<aside class="warning">
 While Synse Server supports the listed Query Parameters, not all devices will support the 
 corresponding actions. As a result, writing to some <i>LED</i> instances may result in error.
</aside>

### Response Fields

See the responses for [read](#read) and [write](#write).


## Fan

> If no *valid* query parameters are specified, this will **read** from the fan device.

```shell
curl "http://host:5000/synse/2.0/fan/rack-1/vec/eb9a56f95b5bd6d9b51996ccd0f2329c"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/fan/rack-1/vec/eb9a56f95b5bd6d9b51996ccd0f2329c')
```

> The response JSON will be the same as read response:

```json
{
  "type": "fan",
  "data": {
    "fan_speed": {
      "value": 0,
      "timestamp": "2018-02-01T17:07:18.113960446Z",
      "unit": {
        "symbol": "RPM",
        "name": "revolutions per minute"
      }
    }
  }
}
```

> If any *valid* query parameters are specified, this will **write** to the fan device.

```shell
curl "http://host:5000/synse/2.0/fan/rack-1/vec/eb9a56f95b5bd6d9b51996ccd0f2329c?speed=200"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/fan/rack-1/vec/eb9a56f95b5bd6d9b51996ccd0f2329c?speed=200')
```

> The response JSON will be the same as a write response:

```json
[
  {
    "context": {
      "action": "speed",
      "raw": [
        "200"
      ]
    },
    "transaction": "b9pkjh8fmg5g01vmt7d0"
  }
]
```

An alias to `read` from or `write` to a known fan device.

While a fan device can be read directly via the [read](#read) route or written to directly from the
[write](#write) route, this route provides some additional checks and validation before dispatching to
the appropriate plugin handler. In particular, it checks if the specified device is a fan device and
that the given query parameter value(s), if any, are permissible.

If no valid query parameters are specified, this endpoint will read the specified device. If any number
of valid query parameters are specified, the endpoint will write to the specified device.

### HTTP Request

`GET http://host:5000/synse/2.0/fan/{rack}/{board}/{device}`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| *rack*    | yes      | The id of the rack containing the fan device to read from/write to. |
| *board*   | yes      | The id of the board containing the fan device to read from/write to. |
| *device*  | yes      | The id of the fan device to read from/write to. |

### Query Parameters

| Parameter | Description |
| --------- | ----------- |
| *speed* | The speed (in RPM) to set the fan to. |
| *speed_percent* | The speed (in percent) to set the fan to. |

<aside class="warning">
 While Synse Server supports the listed Query Parameters, not all devices will support the 
 corresponding actions. As a result, writing to some <i>fan</i> instances may result in error.
</aside>

### Response Fields

See the responses for [read](#read) and [write](#write).
