# Synse Reads
## Summary
This document provides details on the changes to the `/read` endpoint and the
read behavior in Synse more generally.

## High Level Work Items
- Update `/read` [API](api.md#read)
- Add support for group reads
- Update scheme for read response

## Proposal
### Tag-Based Reads
> See: [Tags](tags.md)

***tl;dr** - we will move away from using rack/board/device as the routing mechanism since
it has outlived its intended purpose and move to a tag-based routing system.*

Instead of requiring the `rack/board/device` routing info for a device to read, we will
now filter devices to read via a `tags` query parameter. 


### Multi-Reads/Bulk Reads
> See: [Tags](tags.md)

***tl;dr** - with tags, we can filter on groups, so we can read all devices within a 
group and return those readings simultaneously.* 

With the introduction of [tags](tags.md) as the primary filtering mechanism for devices,
the possibility of selecting multiple devices is opened up. If a tag is associated with
multiple devices, selecting that tag is effectively selecting all those devices. The exception
to this is the `id` tag (TBD what the actual tag key is), which will get only the device with
the specified id, if it exists.

This means that:
- The SDK must be able to filter devices based on tags and return readings for all
  devices that match a set of tags.
- The gRPC API must be updated so that multiple readings can be returned (along with
  any schema changes).
- Synse Server needs an update to the `read` endpoint and the endpoint's JSON response
  (see [Synse Server Read Response](#synse-server-read-response), below) to support
  multiple readings being returned for a single query.

### Read Context

***tl;dr** - some plugins/protocols need a way to associate more information with a reading
than the v2 api allows for, so we need to add contexts to the readings.*

Some protocols may produce data that is only useful if it is associate with a source,
or with other pieces of metadata. An example of this is [sFlow](https://sflow.org/).

In order to associate metadata with a readings or set of readings, an optional `"context"`
field will be added to the reading response (this also affects the gRPC API). The `context`
will be a dictionary that must have a string key and an arbitrary data value.

There is no limit to the number of entries that can be placed into a reading context.

Upstream of Synse Server, the context can be used as the consumer sees fit. A good use
case for it would be to convert the k:v pairs in the context to Prometheus labels for
that particular reading.

The the section below for how the context field is represented in the response scheme.

### Synse Server Read Response
> See: [API: Read](api.md#read)

The read response will need to change, both to support returning multiple readings as
well as to provide additional reading context, if any exists. Directly below is an example
of what a read response looks like in API v2, for reference.

**v2 read response scheme example**
```json
{
  "kind": "temperature",
  "data": [
    {
      "value": 20.3,
      "timestamp": "2018-02-01T13:47:40Z",
      "unit": {
        "symbol": "C",
        "name": "degrees celsius"
      },
      "type": "temperature",
      "info": ""
    }
  ]
}
```

For the v3 read response scheme, we need to:
* support multiple device read responses
  * in addition, we need to include identifying information about the device to know which device
    the reading is associated with. (previously this did not exist because synse-server knew the
    rack/board/device routing for a single device before it read from it, so it had that information
    available -- now we will not, so it needs to be returned in the response).
* optional context for a reading

**v3 read response scheme example**
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
