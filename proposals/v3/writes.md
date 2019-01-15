# Synse Writes
## Summary
This document provides details on the changes to the `/write` endpoint and the
write behavior more generally.

## High Level Work Items
- Update `/write` [API](api.md#write)
- Add support for group writes
- Remove `raw` keyword support from write payload 

## Proposal
### Payload
The JSON payload for a write is similar to what it was in Synse v2. It consists
of:
* **action**: (required) what does the device do?
* **data**: (optional) how does the device do it?

> **Note**: In v2, `raw` was deprecated in favor of `data`, but the `raw` keyword
> was still supported for backwards compatibility. With this major version bump,
> the `raw` keyword will be removed.

An example of this would be changing the color of an LED device
```json
{
  "action": "color",
  "data": "ff00ff"
}
```

The *action* and the *data* required by a write (note: *data* is optional) is defined by
the plugin.

### Query Parameters
In addition to the namespace and tag-based query parameters needed for device routing,
writes will support the following:

#### `transaction`
The *transaction* query parameter allows the caller to specify their own transaction ID
for the write. This is particularly useful for external services (e.g. a frontend) which
would manage and track their own global transaction ids.

If the user-specified transaction id conflicts with something already in the transaction
cache, an error is returned.

### Single Write
Synse v2 only supports single device writes, where the write target is specified
by the standard `rack/board/device` identifier. Synse v3 replaces `rack/board/device`
based routing with [tag-based routing](tags.md).

Any number of devices can be associated with a tag, so Synse v3 will be able to
support [group writes](#group-writes) as well. The reserved `id` (tag name still TBD)
is the exception, as only a single device may be associated with a given `id`; this
allows unique device identification.

> **Note**: This assumes we are able to have [globally unique device ids](ids.md).

To write to a single device, the id must be supplied to the `/write` endpoint
(See: [API Write](api.md#write)). This can be done using the `id` query parameter.
If the provided id is not known, an error is returned.

### Group Writes
*Group Writing* is new in Synse v3 and is enabled by the tag-based routing system.
For a reasonable user experience, limitations are set on which tags can be used to
issue a group write. 

Different devices support a range of different capabilities. It would not make sense
to batch a write to a door lock and an LED. They may not support the same actions, and
even if they did, the behavior of those actions are fundamentally different. Scoping
group writes to the device type provides some level of sanity that (a) the devices
support the same actions, and (b) the devices behave the same way for that action.

Group writes would likely not be used as much as writing to a single device, but supporting
this capability would make it easier to perform various bulk actions in one request, e.g.
turn all lights on/off, lock all doors, etc.

#### Points of Failure
There are many possible points of failure with this approach. All should cause an error
to be returned. Some cases may need pre-processing (e.g. on the SDK side, before adding
items to the write queue) in order to prevent partial writes (where some devices fail and
some succeed).

- one or multiple of the devices do not exist
- one or multiple of the devices do not support the action
- ...


### Multi-Value Writes
Synse v2 only supports writing one action to a device per request. In some cases,
it would be beneficial to be able to send multiple writes in one request. For example,
changing an LED color from green to red and its state from 'on' to 'blink'. This would
take two requests in Synse v2, which opens up the possibility of having one request
succeed and the other fail (e.g. timeout error), so the desired end state is not met.

By allowing multiple action-data pairs to be specified for a single write, Synse will
be able to issue multiple write actions in a single request. This ensures that both
writes will either be received or not received by the plugin simultaneously, making the
error handling for these multi-state changes simpler. 

```json
[
  {
    "action": "color",
    "data": "ff0000"
  },
  {
    "action": "state",
    "data": "blink"
  }
]
```