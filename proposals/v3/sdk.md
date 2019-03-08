# SDK
## Summary
Synse v3 brings a number of changes to Synse, particularly with the modeling and
routing of devices in the system. The SDK will need to be updated to accommodate this.

There are also a number of areas in the SDK that can be improved to make it easier
to use and to make aspects of it less confusing.

## High Level Work Items
- Update device modeling for [tag based routing](tags.md)
- Update plugin configuration to account for new additions, e.g.
  - [health checks](health.md)
  - [plugin id namespaces](ids.md)
  - [monitoring](monitoring.md)
- Simplify configuration and internal modeling where possible
- Improvements to the SDK API
- Plugin health checks
- Update SDK to use the v3 [GRPC API](grpc.md)

## Proposal
Many of the larger work items are discussed in their own documents (see links
above), so this document will not discuss them in further detail. Below are
the additional SDK-specific items to improve SDK usage.

### Remove non-major version checks for config schemes
This has already been started and noted in the [SDK source](https://github.com/vapor-ware/synse-sdk/blob/ee3e84f602c74c6e499a36f7f58916f08eeb74b6/sdk/config.go#L88-L102).
This version check at each individual field was excessive and while interesting
in theory, burdensome in practice. Instead of versioning the fields with a major/minor
version, we should just version the config structs at a major version. Any future
changes to a config struct should always be backwards compatible for that version.

### Profile the SDK
It would be beneficial to profile a set of plugins to determine whether there
are any bottlenecks in the SDK, to verify that its performance matches its expected
behavior (e.g. serial v. parallel), and to identify memory leaks, if any exist.

It would not be necessary to implement any optimizations unless a serious problem
was detected, but having any kind of performance data is useful as it can serve as
a baseline for any future changes.

### Support for configurable plugin health checks
See: [Health](health.md#synse-plugins)

### Update Default Plugin Path
The default plugin path in Synse Server will change - any related pathing changes
in the SDK should be updated as well.

See: [Default Plugin Path](server.md#default-plugin-path)

### Expose additional data for device info
Synse's `/info` endpoint will provide details on what actions a device supports
for writing. This will be surfaced through the [GRPC API](grpc.md#v3device). The
SDK needs a way of defining these in such a manner that the data can be passed up
to Synse Server.

### Adding a plugin configurable write timeout
The SDK should always resolve a write and update the transaction state assuming that
the `Write` interface that it calls resolves. Each plugin will write differently and
have different expectations for how long it may take a write to complete, so we can not
have a single global write timeout; it must be configurable by the plugin to fit within
the expected bounds of the protocol it supports.

If the SDK is writing to a device and the timeout is exceeded, the write should terminate
and the SDK should put that transaction into an error state, where the message specifies
that the write action timed out.

A write could time out for a number of reasons ranging from a hardware failure,
the communication between the plugin and hardware hanging, or the plugin implements
error handling improperly causing it to hang. For example, a plugin communicating
over HTTP may not set a timeout for requests causing it to hang forever. Adding this
functionality will prevent these kinds of failures from:
- keeping a transaction blocked from completing
- blocking the write loop/read loop (especially when configured in serial mode)

The plugin-configured write timeout should be surfaced to Synse Server via the
GRPC API and ultimately exposed through the [Synse API](api.md#transaction) so
any front end consumer can know the maximum time they should wait for the write to
resolve.

There are a number of ways that the write timeout can be defined:
- SDK default (defined in SDK code) (this should be short, perhaps 1-2s?)
- Plugin default (defined in plugin code)
- Plugin override (defined in config)
- Device prototype override (defined in device config)
- Device instance override (defined in device config)

Each item in the list above takes precedence over the item before it.


### Improve `OutputType` design and usage
> **Note**: See [Appendix B](appendix-b.md) for more information on this. This
> section contains some initial high level thoughts, whereas the appendix expands
> upon this and digs deeper down to the implementation level to see how this could
> actually be achieved. Just keeping this section as-is for now for posterity and
> further review.

`OutputType`s have been required in the device configuration as a means of type safety.
Plugin definitions are fairly static and this constraint and added complexity to the
configuration and plugin setup are unnecessary.

Across plugins, there may be similar types defined (e.g. "temperature"), which would
lead to duplicate definitions. While not necessarily bad, it does mean that the way
temperature is defined in one case may differ from another (or there may be an error
in one definition).

To try and simplify how `OutputTypes` are used and to make them more extensible
across plugins, a number of changes can happen:

0. Remove the requirement to specify output types in the device config. (For an
   example, see: [Appendix A-1](appendix-a.md#1-sdk-device-configurations).)
0. Create a "library" of types in the SDK itself, reducing the number of definitions
   a plugin will need to define.
0. Add functionality for common actions on output types, e.g. conversion


The type library would just be a sub-package of the SDK, and would contain common
pre-defined outputs (temperature, humidity, voltage, etc.). Plugins would still have
the ability to define their own output types should they need to.

Extending the `OutputType` to support things like unit conversion would be useful
for setting a measurement system (imperial, metric) or normalizing all readings
across potentially disparate devices to the same unit of measure to add system-wide
consistency.

The system of measure will default to metric. Requests from Synse Server can specify
imperial as the system of measure, if desired. This will be an option passed via the
GRPC API.


### Simplify Device Configuration
Parts of the device configuration for plugins can be confusing, overly verbose,
or at a level of detail that the configurer should not need to care about. Part of this
stems from the consolidation of previous configuration schemes and from the
iterative additions and updates to the SDK after tackling different classes of
plugins.

Various changes can be made to the device configurations both to support the
[tag](tags.md) based routing system, as well as reducing and simplifying the
number of configurable pieces.

* Simplify `kind`
  * The kind does not really need to be as complex as it is (namespaced, final element being
    the type). Its primary function is to provide identity for the device prototype both
    for a user (e.g. human readable) and to match it to a plugin handler. Simplifying this
    will reduce the ambiguity around the `kind`/`type` relationship.
  * It is questionable whether it even needs to be something that an upstream user sees. This
    may only need to be an internal thing. TBD.
  * This could be renamed to `name`?
  * This could probably also be removed entirely if we standardize on using the `handler`
    field to specify the device handler for the device.
* Keep `type` in the device config, but provide a clear updated definition for what
  it actually is.
  * The "type" is really just metadata that is useful to the consumer for grouping devices
    around general behavior. The type of a device doesn't guarantee its capabilities or
    behavior (e.g. one LED could just power on/power off, another one could have on/off/blink
    and allow you to set the color).
  * This needs to remain defined in the config because device handlers are not guaranteed
    to be tied to a specific device. There are generic device handlers which exist (e.g.
    modbus 'input_register').
* Remove `locations` block
  * Will no longer be using `rack/board/device` designation
* Add `tags` config fields
  * Should exist at multiple levels (e.g. global, prototype, instance, ...)
  * In configuration, tags are additive, e.g. an instance's tags add any prototype tags which are defined
* Remove `outputs`, no need to define output types in config
  * The supported output types for a given device really won't change per handler,
    so there is no need for them to be configurable. They can be defined in code
    as part of the device handler struct.
    

For examples of how the configuration would look for different kinds of plugins,
see [Appendix A-1](appendix-a.md#1-sdk-device-configurations).
 
> **TODO**: If the above is accepted, HTTP/GRPC API schemes will need some changes.


> Question: If we are not requiring the device to be tied to any specific outputs
> in the config anymore, can we still surface the OutputTypes that a device returns
> to Synse Server for upstream API consumers?


### Device FQDN/Aliases
See: [Amendment 1: Device FQDN & Aliases](amendment-1.md) 