# Synse v3 WebSocket API
## Summary
Synse v3 adds support for WebSockets to Synse Server. This document describes
the the WebSocket API.

> **Note**: I haven't done much WebSocket API design prior to this. I think
> this proposal is generally fine, but someone with more experience can ultimately
> determine. Some changes may be needed to the process of connecting (and possibly
> authenticating? (see: [Security](security.md)))

## High Level Work Items
- Implement the WebSocket API in Synse Server per this spec.

## Proposal
This section contains the proposed WebSocket API specification for Synse v3.

The response `data` JSON here is similar to that of the [HTTP API](api.md) and is
linked appropriately in order to prevent duplicate definitions for these
documents.

> Synse also exposes an [HTTP API](api.md).

### Connect
```
GET http://HOST:5000/v3/connect
```

Connect to Synse Server, starting the WebSocket session.

If WebSockets are disabled for the instance, this endpoint will accept the WebSocket
connection and immediately close it with a [4000 code](https://tools.ietf.org/html/rfc6455#section-7.4.2).

The client can look at the [CloseEvent](https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent)
code to determine the cause.


### Events
All messages sent over the WebSocket API are considered "events". Generally, there
are two kinds of events: requests (client -> server) and responses (server -> client).
A single request event may trigger multiple response events.

Events are send as JSON. The event object contains metadata about the event. All data
for requests and responses is stored in the `data` field.

```json
{
  "id": 1,
  "event": "response/version",
  "data": {
    "version": "3.0.0",
    "api_version": "v3"
  }
}
```

**Fields**

| Field | Description |
| :---- | :---------- |
| id    | A unique (for the connection) positive integer ID. All responses to a request will include the same ID so a client can easily match a response to its originating request. |
| event | The name of the event. This document specifies supported events in following sections. |
| data  | The data associated with the event. This will be event-specific. |



### Request Events
Below is an accounting of request events supported by the Synse WebSocket API. These events largely
correspond to the [HTTP API routes](api.md#api-endpoints).

Below is a table of contents for the Websocket request/response events.

| Request | Response |
| :------ | :------- |
| [request/status](#status) | [response/status](#status-1) |
| [request/version](#version) | [response/version](#version-1) |
| [request/config](#config) | [response/config](#config-1) |
| [request/plugin](#plugin) | [response/plugin](#plugin-1) |
| [request/plugin_health](#plugin-health) | [response/plugin_health](#plugin-health-1) |
| [request/scan](#scan) | [response/device_summary](#device-summary) |
| [request/tags](#tags) | [response/tags](#tags-1) |
| [request/info](#info) | [response/device](#device) |
| [request/read](#read) | [response/reading](#reading) |
| [request/read_cache](#read-cache) | [response/reading](#reading) |
| [request/write](#write) | [response/write_state](#write-state) |
| [request/transaction](#transaction) | [response/write_state](#write-state) |


#### Status
| | |
| :--- | :--- |
| **Name** | request/status|
| **Description** | Get status information for the Synse Server instance. |
| **Expected Response** | response/status |

##### Event Data
There is no event data for this request. The `data` field is ignored and can be omitted.

```json
{
  "id": 1,
  "event": "request/status"
}
```

#### Version
| | |
| :--- | :--- |
| **Name** | request/version |
| **Description** | Get version information for the Synse Server instance. |
| **Expected Response** | response/version |

##### Event Data
There is no event data for this request. The `data` field is ignored and can be omitted.

```json
{
  "id": 1,
  "event": "request/version"
}
```

#### Config
| | |
| :--- | :--- |
| **Name** | request/config |
| **Description** | Get the operating configuration for the Synse Server instance. |
| **Expected Response** | response/config |

##### Event Data
There is no event data for this request. The `data` field is ignored and can be omitted.

```json
{
  "id": 1,
  "event": "request/config"
}
```

#### Plugin
| | |
| :--- | :--- |
| **Name** | request/plugin |
| **Description** | Get information on the currently registered plugins. |
| **Expected Response** | response/plugin |

##### Event Data
| Field | Type | Required | Description |
| :---- | :--- | :------- | :---------- |
| *plugin* | `string` | no | The ID of the plugin to get more information for. |

```json
{
  "id": 1,
  "event": "request/plugin",
  "data": {
    "plugin": "12835beffd3e6c603aa4dd92127707b5"
  }
}
```

If no plugin ID is provided, this will result in a summary of all registered
plugins.

#### Plugin Health
| | |
| :--- | :--- |
| **Name** | request/plugin_health |
| **Description** | Get a summary of the health of registered plugins. |
| **Expected Response** | response/plugin_health |

##### Event Data
There is no event data for this request. The `data` field is ignored and can be omitted.

```json
{
  "id": 1,
  "event": "request/plugin_health"
}
```


#### Scan
| | |
| :--- | :--- |
| **Name** | request/scan |
| **Description** | List the devices that Synse knows about. |
| **Expected Response** | response/device_summary |

##### Event Data
| Field | Type | Required | Description |
| :---- | :--- | :------- | :---------- |
| *ns* | `string` | no | The default namespace to use for the specified labels. (default: `default`) |
| *tags* | `list[string]` | no | The tags to filter devices on. |
| *force* | `bool` | no | Force a re-scan of the plugin devices. |

```json
{
  "id": 1,
  "event": "request/scan",
  "data": {
    "tags": [
      "foobar"
    ]
  }
}
```

All data fields for this event are optional. If none are specified, `data` can
be omitted entirely.


#### Tags
| | |
| :--- | :--- |
| **Name** | request/tags |
| **Description** | List all tags which are currently associated with devices. |
| **Expected Response** | response/tags |

##### Event Data
| Field | Type | Required | Description |
| :---- | :--- | :------- | :---------- |
| *ns* | `list[string]` | no | The tag namespace(s) to use when searching for tags. (default: `[default]`) |
| *ids* | `bool` | no | Include ID tags in the response. (default: `false`) |

```json
{
  "id": 1,
  "event": "request/tags",
  "data": {
    "ns": [
      "vapor", 
      "synse"
    ]
  }
}
```

All data fields for this event are optional. If none are specified, `data` can
be omitted entirely.


#### Info
| | |
| :--- | :--- |
| **Name** | request/info |
| **Description** | Get the full set of metadata for a device. |
| **Expected Response** | response/device |

##### Event Data
| Field | Type | Required | Description |
| :---- | :--- | :------- | :---------- |
| *device* | `string` | yes | The GUID of the device to get info for. |

```json
{
  "id": 1,
  "event": "request/info",
  "data": {
    "device": "34c226b1afadaae5f172a4e1763fd1a6"
  }
}
```


#### Read
| | |
| :--- | :--- |
| **Name** | request/read |
| **Description** | Read data from a device or devices. |
| **Expected Response** | response/reading |

##### Event Data
| Field | Type | Required | Description |
| :---- | :--- | :------- | :---------- |
| *ns* | `string` | no | The default namespace to use for the specified labels. (default: `default`) |
| *tags* | `list[string]` | yes | The tag(s) to filter devices on. |

```json
{
  "id": 1,
  "event": "request/read",
  "data": {
    "tags": [
      "id:34c226b1afadaae5f172a4e1763fd1a6"
    ]
  }
}
```

#### Read Cache
| | |
| :--- | :--- |
| **Name** | request/read_cache |
| **Description** | Read data from a device or devices. |
| **Expected Response** | response/reading |

##### Event Data
| Field | Type | Required | Description |
| :---- | :--- | :------- | :---------- |
| *start* | `string` | no | An RFC3339 formatted timestamp which specifies a starting bound on the cache data to return. |
| *end* | `string` | no | An RFC3339 formatted timestamp which specifies an ending bound on the cache data to return. |

If no timestamp is specified, there will not be an starting/ending bound.

```json
{
  "id": 1,
  "event": "request/read_cache",
  "data": {
    "start": "2018-02-01T13:47:40Z",
    "end": "2018-02-01T13:47:40Z"
  }
}
```

#### Write
| | |
| :--- | :--- |
| **Name** | request/write |
| **Description** | Write data to a device. |
| **Expected Response** | response/write_state |

##### Event Data
| Field | Type | Required | Description |
| :---- | :--- | :------- | :---------- |
| *device* | `string` | yes | The GUID of the device that is being written to. |
| *action* | `string` | yes | The action that the device will perform. This is set at the plugin level. |
| *data* | `bytes` | sometimes | Any data that an *action* may require. Not all actions require data. This is plugin-defined. |
| *transaction* | `string` | no | A user-defined transaction ID for the write. This allows the write to be checked later, e.g. in case of failure. |

```json
{
  "id": 1,
  "event": "request/write",
  "data": {
    "device": "34c226b1afadaae5f172a4e1763fd1a6",
    "action": "color",
    "data": "ff00ff",
    "transaction": "56a32eba-1aa6-4868-84ee-fe01af8b2e6d"
  }
}
```


#### Transaction
| | |
| :--- | :--- |
| **Name** | request/transaction |
| **Description** | Get the state of a write from transaction ID. |
| **Expected Response** | response/write_state |

##### Event Data
| Field | Type | Required | Description |
| :---- | :--- | :------- | :---------- |
| *transaction* | `string` | yes | The transaction ID for the write. Generally, this will only need to be checked if a write fails to return any state. |

```json
{
  "id": 1,
  "event": "request/transaction",
  "data": {
    "transaction": "56a32eba-1aa6-4868-84ee-fe01af8b2e6d"
  }
}
```



### Response Events
Response events correspond to the responses in the [Synse HTTP API](api.md). All response messages
will have an ID field which contains the ID of the event which triggered the response.

> **NOTE**: For many of the field descriptions, see the [HTTP API](api.md) document. They
> are intentionally left blank here to avoid having to maintain two copies of the same info.


#### Status
| | |
| :--- | :--- |
| **Name** | response/status|
| **Description** | The status information of a Synse Server instance. |

##### Event Data
| Field | Type | Required | Description |
| :---- | :--- | :------- | :---------- |
| *status* | `string` | yes | "ok" if the endpoint returns successfully. |
| *timestamp* | `string` | yes | The time at which the status was tested. |


```json
{
  "id": 1,
  "event": "response/status",
  "data": {
    "status": "ok",
    "timestamp": "2018-11-09T14:32:47Z"
  }
}
```


#### Version
| | |
| :--- | :--- |
| **Name** | response/version |
| **Description** | The version information of a Synse Server instance. |

##### Event Data
| Field | Type | Required | Description |
| :---- | :--- | :------- | :---------- |
| *version* | `string` | yes | - |
| *api_version* | `string` | yes | - |


```json
{
  "id": 1,
  "event": "response/version",
  "data": {
    "version": "3.0.0",
    "api_version": "v3"
  }
}
```


#### Config
| | |
| :--- | :--- |
| **Name** | response/config |
| **Description** | The Synse Server instance configuration. |

##### Event Data
> *Note*: Fields and description omitted here, see the Synse Server config scheme.


```json
{
  "id": 1,
  "event": "response/config",
  "data": {
    ...
  }
}
```


#### Plugin
| | |
| :--- | :--- |
| **Name** | response/plugin |
| **Description** | Information on a Synse Plugin. |

##### Event Data
> *Note*: See [HTTP API: Plugin](api.md#plugins) Response scheme.

```json
{
  "id": 1,
  "event": "response/plugin",
  "data": {
    ...
  }
}
```


#### Plugin Health
| | |
| :--- | :--- |
| **Name** | response/plugin_health |
| **Description** | Health summary of all plugins. |

##### Event Data
> *Note*: See [HTTP API: Plugin Health](api.md#plugin-health) Response.


```json
{
  "id": 1,
  "event": "response/plugin_health",
  "data": {
    ...
  }
}
```


#### Tags
| | |
| :--- | :--- |
| **Name** | response/tags |
| **Description** | A list of device tags. |

##### Event Data
| Field | Type | Required | Description |
| :---- | :--- | :------- | :---------- |
| *tags* | `list[string]` | yes | - |


```json
{
  "id": 1,
  "event": "response/tags",
  "data": {
    "tags": [
      "default/tag1",
      "default/type:temperature"
    ]
  }
}
```


#### Device
| | |
| :--- | :--- |
| **Name** | response/device |
| **Description** | Information for a device. |

##### Event Data
> *Note*: See [HTTP API: Info](api.md#info) Response.


```json
{
  "id": 1,
  "event": "response/device",
  "data": {
    ...
  }
}
```


#### Device Summary
| | |
| :--- | :--- |
| **Name** | response/device_summary |
| **Description** | A summary of device information. |

##### Event Data
> *Note*: See [HTTP API: Scan](api.md#scan) Response.


```json
{
  "id": 1,
  "event": "response/device_summary",
  "data": [
    ...
  ]
}
```


#### Reading
| | |
| :--- | :--- |
| **Name** | response/reading |
| **Description** | A single device reading. |

##### Event Data
> *Note*: See [HTTP API: Read](api.md#read) Response.


```json
{
  "id": 1,
  "event": "response/reading",
  "data": [
    ...
  ]
}
```


#### Write State
| | |
| :--- | :--- |
| **Name** | response/write_state |
| **Description** | The state for a write action. |

##### Event Data
> *Note*: See [HTTP API: Transaction](api.md#transaction) Response.


```json
{
  "id": 1,
  "event": "response/write_state",
  "data": {
    ...
  }
}
```


#### Error
| | |
| :--- | :--- |
| **Name** | response/error |
| **Description** | A Synse error. |

##### Event Data
> *Note*: See [HTTP API: Errors](api.md#errors) Response.


```json
{
  "id": 1,
  "event": "response/error",
  "data": {
    "http_code": 404,
    "description": "Device not found",
    "timestamp": "2018-01-24 19:22:28Z",
    "context": "f52d29fecf05a195af13f14c73065252d does not correspond with a known device ID"
  }
}
```
