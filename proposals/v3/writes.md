# Synse Writes
## Summary
This document provides details on the changes to the `/write` endpoint and the
write behavior more generally.

## High Level Work Items
- Update `/write` [API](api.md#write)
- Add support for group writes

## Proposal
### Payload
The JSON payload for a write is similar to what it was in Synse v2. It consists
of:
* **action**: (required) what does the device do?
* **data**: (optional) how does the device do it?

An example of this would be changing the color of an LED device
```json
{
  "action": "color",
  "data": "ff00ff"
}
```

The *action* and the *data* it requires (if it requires data at all) is defined by the
plugin.

> **Question**: Is the "action", "data" naming intuitive enough, or are there
> better names for the fields? Suggestions welcome.


### Single Write
Synse v2 only supports single device writes, where the write target is specified
by the standard `rack/board/device` identifier. Synse v3 replaces `rack/board/device`
based routing with [tag-based routing](tags.md).

Any number of devices can be associated with a tag, so Synse v3 will be able to
support [group writes](#group-writes) as well. The reserved `id` (tag name still TBD)
is the exception, as only a single device may be associated with a given `id`; this
allows unique device identification.

> **Note**: This assumes we are able to have globally unique device ids.

To write to a single device, the id must be supplied to the `/write` endpoint. (TBD
on whether this is an `?id` query param, or a "single device write" endpoint `/write/{device}`).
If the provided id does not exist/is not associated with a known device, an error
will be returned.


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

> **Question**: It isn't clear what the best approach for this is, but it would
> likely require a change to the payload data.

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