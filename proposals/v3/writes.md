# Synse Writes
## Summary
This document provides details on the changes to the `/write` endpoint and the
write behavior more generally.

## High Level Work Items
- Update `/write` [API](api.md#write-asynchronous)
- Add synchronous write capabilities
- Add support for batch writes
- Remove `raw` keyword support from write payload 

## Proposal
### Payload
The JSON payload for a write is similar to what it was in Synse v2. It consists
of:
* **action**: (required) The action which the device performs. This is defined
  at the plugin level.
* **data**: (optional) Additional data that is needed for the write action.

> **Note**: In v2, `raw` was deprecated in favor of `data`, but the `raw` keyword
> was still supported for backwards compatibility. With this major version bump,
> support for the `raw` keyword will be removed.

An example of this would be changing the color of an LED device
```json
{
  "action": "color",
  "data": "ff00ff"
}
```

The values for both *action* and *data* are defined by the plugin which manages a
particular device. The supported actions for a device write are surfaced in Synse
Server by the [`/info`](api.md#info) endpoint.

### Query Parameters
#### `transaction`
The *transaction* query parameter allows the caller to specify their own transaction ID
for the write. This is particularly useful for external services (e.g. a frontend) which
would manage and track their own global transaction ids.

If the user-specified transaction id conflicts with something already in the transaction
cache, an error is returned.

### Single Write
Synse v3, like v2, will only support single writes. Group writes using arbitrary tags
was considered, but ultimately rejected because of the added complexity it would add,
particularly around partial write failures and state tracking.

Since [device IDs](ids.md) are globally unique in Synse v3, only the device ID is needed
to route a write request to a particular device.

For more, see the [API write](api.md#write-asynchronous) endpoint. 

### Batch Writes
For convenience and to reduce the number of network requests needed to issue multiple
writes (e.g. changing color and state of all lights on a Vapor Chamber), v3 adds
batch write functionality.

Writes are batched by including multiple write contexts in the POSTed body of the
write, e.g.

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

Furthermore, if the caller wants to specify their own transaction ID for the batched
writes, they can do so in the POST body as well.

```json
[
  {
    "action": "color",
    "data": "f38ac2",
    "transaction": "56a32eba-1aa6-4868-84ee-fe01af8b2e6d"
  },
  {
    "action": "state",
    "data": "blink",
    "transaction": "56a32eba-1aa6-4868-84ee-fe01af8b2e6e"
  }
]
``` 

It is important to note that these write are still handled as individual write actions
and each gets their own transaction ID. It is up to the caller to track and check each
of these transactions. 

