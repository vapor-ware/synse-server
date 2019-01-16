# SDK
## Summary
Synse v3 brings a number of changes to Synse, particularly with the modeling and
routing of devices in the system. The SDK will need to be updated to accommodate this.
Additionally, there are a number of areas in the SDK that could be improved upon.

## High Level Work Items
- Update device modeling for [tag based routing](tags.md)
- Update plugin configuration to account for new additions, e.g.
  - [health checks](health.md)
  - [plugin id namespaces](ids.md)
  - [monitoring](monitoring.md)
- Improvements to the SDK API
- Plugin health checks

## Proposal
Many of the larger work items are discussed in their own documents (see links
above), so this document will not discuss them in further detail. Below are
the additional SDK-specific items to improve SDK usage.

### Remove non-major version checks for config schemes
This has already been started and noted in the [SDK source](https://github.com/vapor-ware/synse-sdk/blob/ee3e84f602c74c6e499a36f7f58916f08eeb74b6/sdk/config.go#L88-L102).
This version check at each individual field was excessive and while interesting
in theory, burdensome in practice. Instead of versioning the fields with a major/minor
version, we should just version the config structs at a major version. Any changes
to an existing config struct should always be backwards compatible for that version.

### Remove requirement to specify output type per device in config
The SDK currently requires the device config to specify the supported output types
for a given device kind, e.g.
```yaml
devices:
  - name: humidity
    metadata:
      model: emul8-humidity
    outputs:
      - type: humidity
      - type: temperature
```

This isn't too bad in some cases, like the one above, but once the complexities of
things like dynamic registration (e.g. IPMI, SNMP), extensive non-homogeneous device
configuration (e.g. Modbus-IP), variable push-driven metrics (sFlow) are taken into
account, this feature becomes burdensome and does not provide us with much.

The initial idea was to include it as a means of "type safety" for an output of a
device, but since plugin definitions are relatively static and the output type of
a device generally should not change, it now seems superfluous to mandate that the
outputs be defined for each supported device type.

Instead, we can just define outputs as we currently do (either directly in the
plugin code, or as a separate config file, or both) and when constructing the
device reading for a given type, look at the global pool of available output
types, not just the ones specifically configured for the device.

This would also allow us to define generic output types directly in the SDK that all
plugins could use without having to define their own. This could make authoring a
plugin easier.

### Profile the SDK
It would be beneficial to profile a set of plugins to determine whether there
are any bottlenecks in the SDK, to verify that its performance matches its expected
behavior (e.g. serial v. parallel), and to identify memory leaks, if any exist.

It would not be necessary to implement any optimizations unless a serious problem
was detected, but having any kind of performance data is useful as it can serve as
a baseline for any future changes.

### Support for plugin health checks
See: [Health](health.md#synse-plugins)