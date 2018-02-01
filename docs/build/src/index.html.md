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

Synse Server provides a simple JSON API to monitor and control data center and IT equipment. More
generally, it provides a uniform interface for backends implementing various protocols, such as
RS485 and I2C. The Synse Server API makes it easy to read from and write to devices, gather device
information, and scan for configured devices through a curl-able interface.



# Endpoints

## Test

```shell
curl "host:5000/synse/test"
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
with the JSON as described below. If the test endpoint is unreachable or otherwise fails, it will return
a 500 response. This is indicative of Synse Server not being up and serving. The test endpoint does not
have any internal dependencies.

### HTTP Request

`GET http://host:5000/synse/test`

### Response Fields

| Field | Description |
| ----- | ----------- |
| status | "ok" if the endpoint returns successfully. |
| timestamp | The time at which the status was tested. |



## Version

```shell
curl "host:5000/synse/version"
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

Get the API version of the Synse Server instance. This version info can be used to ensure the correct
request URI schema and version are being used for a given Synse Server instance.

### HTTP Request

`GET http://host:5000/synse/version`

### Response Fields

| Field | Description |
| ----- | ----------- |
| version | The full version (major.minor.micro) of the Synse Server instance. |
| api_version | The API version (major.minor) that can be used to construct subsequent API requests. |


## Config

```shell
curl "host:5000/synse/2.0/config"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/config')
```

> The response JSON would be structured as:

```json
{
  "locale": "en_US",
  "pretty_json": true,
  "logging": "debug",
  "cache": {
    "meta": {
      "ttl": 20
    },
    "transaction": {
      "ttl": 20
    }
  },
  "grpc": {
    "timeout": 20
  },
  "lang": "en_US"
}
```

Get the current Synse Server configuration.

This is added as a convenience to make it easier to determine what configuration Synse Server is running 
with. Since configuration in Synse Server 1.X was difficult, this endpoints aims to make configuration 
more user-friendly in Synse Server 2.0.

### HTTP Request

`GET http://host:5000/synse/2.0/config`

### Response

The response to the `config` endpoint should be the unified configuration for Synse Server. The 
unified config is the three layers of merged configuration (default, file, environment).

See [the Synse Server configuration documentation]() for more info on how to configure Synse Server
as well as what you can expect from this response.



## Scan

```shell
curl "host:5000/synse/2.0/scan"
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

Enumerate all known racks, boards, and devices accessible by Synse.

This aggregates the known configured racks, boards, and devices for each of the configured plugins providing
information to Synse Server. The scan response provides a high level view of which devices exist to the system
and where they exist. With a scan response, a user should have enough routing information to perform any
subsequent command (e.g. read, write) for a given device.

### HTTP Request

`GET http://host:5000/synse/2.0/scan`

### Query Parameters

| Parameter | Default | Description |
| --------- | ------- | ----------- |
| force     | false   | Force a re-scan of all known devices. This invalidates the existing cache, causing it to be rebuilt. *Valid values:* `true` |

### Response Fields

| Field | Description |
| ----- | ----------- |
| racks | A list of objects which represent a rack. |
| {rack}.id | The primary identifier for the rack. |
| {rack}.boards | A list of board object which belong to the rack. |
| {board}.id | The primary identifier for the board. |
| {board}.devices | A list of device objects which belong to the board. |
| {device}.id | The primary identifier for the device. |
| {device}.info | Any notational information associated with the device to help identify it in a more human-readble way. |
| {device}.type | The type of the device. |


## Read

```shell
curl "host:5000/synse/2.0/read/rack-1/vec/eb100067acb0c054cf877759db376b03"
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
      "timestamp": "2018-02-01 13:47:40.395939895 +0000 UTC m=+719.678352123",
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
      "timestamp": "2018-02-01 13:48:59.573898829 +0000 UTC m=+798.856304661",
      "unit": null
    },
    "color": {
      "value": "000000",
      "timestamp": "2018-02-01 13:48:59.573898829 +0000 UTC m=+798.856304661",
      "unit": null
    },
    "blink": {
      "value": "steady",
      "timestamp": "2018-02-01 13:48:59.573898829 +0000 UTC m=+798.856304661",
      "unit": null
    }
  }
}
```

Read data from a known device.

Devices are made known to Synse Server via the internal gRPC metainfo request on the configured plugins.
This information is surfaced to the user via the scan route. If the specified device supports reading (as
determined by the plugin that manages the device), it will return a read response. Otherwise, an error is
returned stating that reads are not permitted on the type of the given device. 

### HTTP Request

`GET http://host:5000/synse/2.0/read/{rack}/{board}/{device}`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| rack      | yes      | The id of the rack containing the device to read. |
| board     | yes      | The id of the board containing the device to read. |
| device    | yes      | The id of the device to read. |

These values can be found via the [Scan](#scan) command.

### Response Fields

| Field | Description |
| ----- | ----------- |
| type  | The type of the device that was read. |
| data  | An object where the keys specify the reading type and the values are corresponding reading objects. |
| {reading}.value | The value for the given reading type. |
| {reading}.timestamp | The time at which the reading was taken. |
| {reading}.unit | The unit of measure for the reading. If the reading has no unit, this will be `null`. |
| {unit}.name | The long name of the unit. *(e.g. "acceleration")* |
| {unit}.symbol | The symbol (or short name) of the unit. *(e.g. m/s^2)* |


## Write

```shell
curl \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{"action": "color", "raw": "f38ac2"}' \
  "host:5000/synse/2.0/write/rack-1/vec/f52d29fecf05a195af13f14c7306cfed"
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

Devices are made known to Synse Server via the internal gRPC metainfo request on the configured plugins.
This information is surfaced to the user via the scan route. If the specified device supports writing (as
determined by the plugin that manages the device), it will return a write response. Otherwise, an error is
returned stating that writes are not permitted on the type of the given device. 

### HTTP Request

`POST http://host:5000/synse/2.0/write/{rack}/{board}/{device}`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| rack      | yes      | The id of the rack containing the device to write to. |
| board     | yes      | The id of the board containing the device to write to. |
| device    | yes      | The id of the device to write to. |

These values can be found via the [Scan](#scan) command.

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
| action | The write action to perform. This is device-specific. |
| raw | The data associated with the given action. |

The valid values and requirements for `action` and `raw` are dependent on the device type. For
example, an `LED` device supports the actions: `color`, `state`, `blink`; a `fan` device supports
`speed`. 

### Response Fields

| Field | Description |
| ----- | ----------- |
| context | The write payload that was POSTed. This is included to help make transactions more identifiable. |
| timestamp | The time at which the write transaction was issued. |
| transaction | The ID of the write transaction. Each write will have its own ID. The status of a transaction can be checked with the [transaction](#transaction) command. |


## Transaction

```shell
curl "host:5000/synse/2.0/transaction/b9pin8ofmg5g01vmt77g"
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
  "created": "2018-02-01 15:00:51.132823149 +0000 UTC m=+4819.558707806",
  "updated": "2018-02-01 15:00:51.132823149 +0000 UTC m=+4819.558707806",
  "message": ""
}
```

Check the status of a write transaction.

### HTTP Request

`GET http://host:5000/synse/2.0/transaction/{transaction id}`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| transaction id | yes | The ID of the write transaction to get the status of. |

### Response Fields

| Field | Description |
| ----- | ----------- |
| id      | The ID of the transaction. |
| context | The POSTed write data for the given write transaction. |
| state   | The current state of the transaction. *Valid values:* (`ok`,`error`) |
| status  | The current status of the transaction. *Valid values:* (`unknown`,`pending`,`writing`,`done`)|
| created | The time at which the transaction was created (e.g. the write issued). |
| updated | The last time the state or status was updated for the transaction. If the transaction has state `ok` and status `done`, no further updates will happen. |
| message | Any context information for the transaction relating to its error state. |


## Info

> The `info` endpoint will return different responses based on the scope of the request. For 
> a rack-level request:

```shell
curl "host:5000/synse/2.0/info/rack-1"
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
curl "host:5000/synse/2.0/info/rack-1/vec"
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
curl "host:5000/synse/2.0/info/rack-1/vec/db1e5deb43d9d0af6d80885e74362913"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/info/rack-1/vec/db1e5deb43d9d0af6d80885e74362913')
```

> The response JSON would be structured as:

```json
{
  "timestamp": "2018-02-01 15:29:31.934013127 +0000 UTC m=+6540.359897686",
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

Get any information on the specified resource.

This command replaces what used to be the “host info” and “asset info” command in Synse v1.3. While the
response here does not mirror a union of the two previous commands’ responses, it does provide a generalized
information scheme that can be applied to all devices of any backend protocol, whereas before host/asset info
were tightly coupled with IPMI responses.

### HTTP Request

`GET http://host:5000/synse/2.0/info/{rack}/{board}/{device}`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| rack      | yes      | The id of the rack to get info for. |
| board     | no       | The id of the board to get info for. Required only if specifying device. |
| device    | no       | The id of the device to get info for. |

### Response Fields

***Rack Level Response***

| Field | Description |
| ----- | ----------- |
| rack  | The ID of the rack. |
| boards | A list of IDs for boards that belong to the rack. |

***Board Level Response***

| Field | Description |
| ----- | ----------- |
| board | The ID of the board. |
| location | An object which provides information on its hierarchical parents (e.g. rack). |
| devices | A list of IDs for devices that belong to the board. |

***Device Level Response***

| Field | Description |
| ----- | ----------- |
| timestamp | The time at which the device info was last retrieved. |
| uid | The unique (per board) ID of the device. |
| type | The type of the device. |
| model | The model of the device, as set in the plugin prototype configuration. |
| manufacturer | The manufacturer of the device, as set in the plugin prototype configuration. |
| protocol | The protocol by which we interface with the device. |
| info | Any human-readable information set to help identify the given device. |
| comment | Any additional comment set for the given device. |
| location | An object which provides information on its hierarchical parents (e.g. rack, board). |
| output | The specification for how the device's reading(s) should be output. |



## LED

> If no query parameters are specified, this will **read** from the LED device.

```shell
curl "host:5000/synse/2.0/led/rack-1/vec/f52d29fecf05a195af13f14c7306cfed"
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
      "timestamp": "2018-02-01 16:16:04.884816422 +0000 UTC m=+8757.873875085",
      "unit": null
    },
    "color": {
      "value": "f38ac2",
      "timestamp": "2018-02-01 16:16:04.884816422 +0000 UTC m=+8757.873875085",
      "unit": null
    },
    "blink": {
      "value": "steady",
      "timestamp": "2018-02-01 16:16:04.884816422 +0000 UTC m=+8757.873875085",
      "unit": null
    }
  }
}
```

> If any valid query parameters are specified, this will **write** to the LED device.

```shell
curl "host:5000/synse/2.0/led/rack-1/vec/f52d29fecf05a195af13f14c7306cfed?color=00ff00&state=on"
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


Read from or write to a known LED device.

While an LED device can be read directly via the read route or written to directly from the write route,
this route provides some additional checks and validation before dispatching to the appropriate route. In
particular, it checks if the specified device is an LED device and that the given values (if any) are
permissible.

If no query parameters are specified, this endpoint will read the specified device. If any number of valid
query parameters are specified, the endpoint will write to the specified device.

### HTTP Request

`GET http://host:5000/synse/2.0/led/{rack}/{board}/{device}`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| rack      | yes      | The id of the rack containing the device to read from/write to. |
| board     | yes      | The id of the board containing the device to read from/write to. |
| device    | yes      | The id of the device to read from/write to. |

### Query Parameters

| Parameter | Description |
| --------- | ----------- |
| state     | The state of the LED. *Valid values:* (`on`,`off`) |
| blink     | The blink state of the LED. *Valid values:* (`blink`,`steady`) |
| color     | The color of the LED. This must be an RGB hexadecimal color string. |

<aside class="notice">
 While Synse Server supports the listed Query Parameters, not all devices will support the 
 corresponding actions. As a result, writing to some <i>LED</i> instances may result in error.
</aside>

### Response Fields

See the responses for [read](#read) and [write](#write).


## Fan

> If no query parameters are specified, this will **read** from the fan device.

```shell
curl "host:5000/synse/2.0/fan/rack-1/vec/eb9a56f95b5bd6d9b51996ccd0f2329c"
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
      "timestamp": "2018-02-01 17:07:18.113960446 +0000 UTC m=+11831.103017007",
      "unit": {
        "symbol": "RPM",
        "name": "revolutions per minute"
      }
    }
  }
}
```

> If any valid query parameters are specified, this will **write** to the fan device.

```shell
curl "host:5000/synse/2.0/fan/rack-1/vec/eb9a56f95b5bd6d9b51996ccd0f2329c?speed=200"
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

Read from or write to a known fan device.

While a fan device can be read directly via the read route or written to directly from the write route,
this route provides some additional checks and validation before dispatching to the appropriate route. In
particular, it checks if the specified device is a fan device and that the given values (if any) are
permissible.

If no query parameters are specified, this endpoint will read the specified device. If any number of
valid query parameters are specified, the endpoint will write to the specified device.

### HTTP Request

`GET http://host:5000/synse/2.0/fan/{rack}/{board}/{device}`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| rack      | yes      | The id of the rack containing the device to read from/write to. |
| board     | yes      | The id of the board containing the device to read from/write to. |
| device    | yes      | The id of the device to read from/write to. |

### Query Parameters

| Parameter | Description |
| --------- | ----------- |
| speed | The speed to set the fan to. |

<aside class="notice">
 While Synse Server supports the listed Query Parameters, not all devices will support the 
 corresponding actions. As a result, writing to some <i>fan</i> instances may result in error.
</aside>

### Response Fields

See the responses for [read](#read) and [write](#write).


## Boot Target

> If no query parameters are specified, this will **read** from the system device.

```shell
curl "host:5000/synse/2.0/boot_target/rack-1/vec/--"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/boot_target/rack-1/vec/--')
```

> The response JSON will be the same as read response:

```json
TODO
```

> If any valid query parameters are specified, this will **write** to the system device.

```shell
curl "host:5000/synse/2.0/boot_target/rack-1/vec/--?target=pxe"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/boot_target/rack-1/vec/--?target=pxe')
```

> The response JSON will be the same as a write response:

```json

```

Read from or write to a known boot target (system) device.

While a boot target (system) device can be read directly via the read route or written to directly from the
write route, this route provides some additional checks and validation before dispatching to the appropriate
route. In particular, it checks if the specified device is a system device and that the given values (if any)
are permissible.

If no query parameters are specified, this endpoint will read the specified device. If any number of valid
query parameters are specified, the endpoint will write to the specified device.

### HTTP Request

`GET http://host:5000/synse/2.0/boot_target/{rack}/{board}/{device}`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| rack      | yes      | The id of the rack containing the device to read from/write to. |
| board     | yes      | The id of the board containing the device to read from/write to. |
| device    | yes      | The id of the device to read from/write to. |

### Query Parameters

| Parameter | Description |
| --------- | ----------- |
| target | The boot target to set. *Valid values:* (`pxe`,`hdd`) |

<aside class="notice">
 While Synse Server supports the listed Query Parameters, not all devices will support the 
 corresponding actions. As a result, writing to some <i>system</i> instances may result in error.
</aside>

### Response Fields

See the responses for [read](#read) and [write](#write).


## Power

> If no query parameters are specified, this will **read** from the power device.

```shell
curl "host:5000/synse/2.0/power/rack-1/vec/--"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/power/rack-1/vec/--')
```

> The response JSON will be the same as read response:

```json

```

> If any valid query parameters are specified, this will **write** to the power device.

```shell
curl "host:5000/synse/2.0/power/rack-1/vec/--?state=cycle"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/power/rack-1/vec/--?state=cycle')
```

> The response JSON will be the same as a write response:

```json

```

Read from or write to a known power device.

While a power device can be read directly via the read route or written to directly from the write route,
this route provides some additional checks and validation before dispatching to the appropriate route. In
particular, it checks if the specified device is a power device and that the given values (if any) are
permissible.

If no query parameters are specified, this endpoint will read the specified device. If any number of valid
query parameters are specified, the endpoint will write to the specified device.

### HTTP Request

`GET http://host:5000/synse/2.0/power/{rack}/{board}/{device}`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| rack      | yes      | The id of the rack containing the device to read from/write to. |
| board     | yes      | The id of the board containing the device to read from/write to. |
| device    | yes      | The id of the device to read from/write to. |

### Query Parameters

| Parameter | Description |
| --------- | ----------- |
| state | The power state to set. *Valid values:* (`on`,`off`,`cycle`) |

<aside class="notice">
 While Synse Server supports the listed Query Parameters, not all devices will support the 
 corresponding actions. As a result, writing to some <i>power</i> instances may result in error.
</aside>

### Response Fields

See the responses for [read](#read) and [write](#write).


## Lock

> If no query parameters are specified, this will **read** from the lock device.

```shell
curl "host:5000/synse/2.0/lock/rack-1/vec/--"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/lock/rack-1/vec/--')
```

> The response JSON will be the same as read response:

```json

```

> If any valid query parameters are specified, this will **write** to the lock device.

```shell
curl "host:5000/synse/2.0/lock/rack-1/vec/--?state=lock"
```

```python
import requests

response = requests.get('http://host:5000/synse/2.0/lock/rack-1/vec/--?state=lock')
```

> The response JSON will be the same as a write response:

```json

```

### HTTP Request

`GET http://host:5000/synse/2.0/lock/{rack}/{board}/{device}`

### URI Parameters

| Parameter | Required | Description |
| --------- | -------- | ----------- |
| rack      | yes      | The id of the rack containing the device to read from/write to. |
| board     | yes      | The id of the board containing the device to read from/write to. |
| device    | yes      | The id of the device to read from/write to. |

### Query Parameters

| Parameter | Description |
| --------- | ----------- |
| state | The lock state of the lock device. *Valid values:* (`lock`,`unlock`) |

<aside class="notice">
 While Synse Server supports the listed Query Parameters, not all devices will support the 
 corresponding actions. As a result, writing to some <i>lock</i> instances may result in error.
</aside>

### Response Fields

See the responses for [read](#read) and [write](#write).

