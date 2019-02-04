# Device IDs
## Summary
A core design component of Synse v2 is the notion of deterministic device IDs. Because all
Synse components are designed to run as Docker-ized services, which may be scheduled on different
machines in various topologies, it is critical that Synse be able to reliably identify a device
across different service instances. This allows the captured time-series data to always be
correctly associated with its source. 

In Synse v2, the device ID alone is not globally unique, but in combination with the corresponding
rack ID and board ID, it is -- hence the `rack/board/device` routing hierarchy.

The [tag-based routing system](tags.md) introduced in Synse v3 will continue to support addressing
devices individually, so the requirement for having a deterministic globally unique device ID
remains unchanged. This document describes how such an identifier will be generated.

## High Level Work Items
- Add SDK configuration modeling for plugin namespacing
- Add SDK support for parsing and verifying the namespace config
- Update the logic for generating device IDs to include the plugin namespace

## Proposal
### Overview
Each plugin will have a deterministic unique namespace, within which all deterministic device IDs
will be generated. The combination of the two ensures that all devices IDs within a single Synse
deployment will be globally unique. See also: [RFC4122 section 4.3](https://tools.ietf.org/html/rfc4122#section-4.3).

The process of generating a unique deterministic ID for a device is already done by the plugin,
so this document will not go into detail on that process.

The process of assigning each plugin a unique namespace is the primary focus of this document.

### Plugin Namespaces
The source of a plugin namespace will depend on the deployment strategy of that plugin. This does
not mean that it depends on what is running/managing the plugin (e.g. docker, kubernetes, systemd,
something else, ...). It means that it depends on:
- Where the plugin will run (bound to a single machine, schedule-able across multiple machines)
- How many instances of the plugin will be running.

To break down the use cases a bit further:

1. The plugin is bound to the machine *(examples: runs as k8s DaemonSet, runs directly on host)*
   - In this case, the machine ID (or any other machine-specific property, like
     static IP) may be used as the primary component of the plugin namespace.
     - *Caveat*: With plugins being run in containers, this information will need to passed
       from the host to the container (ENV, volume mounting, ...)
2. The plugin is not bound to a machine (can be scheduled anywhere) and will only have a **single**
instance running at any given time.
   - This is likely the most frequent use case.
   - In this case, plugin metadata (e.g. the plugin *tag*) may be used as the primary component of
     the plugin namespace.
3. The plugin is not bound to a machine (can be scheduled anywhere) and may have any number
of instances running at a given time (1..N). *(e.g. multiple IPMI plugins for different customers)*
   - **TODO**
   - This could be as simple as specifying an additional field in the Plugin configuration and
     requiring it be filled in which defines a name/identifier/description for the instance, e.g.
     `desc: "Modbus-IP for Chamber-wide power metering"`
4. There are multiple instances of a plugin which can be scheduled anywhere and are load-balancing
against the same backend devices.
   - *This is outside the scope of Synse v3* as there is no current plugin which demonstrates this.
   - The solution would be similar to #2, since the devices would remain the same, regardless of
     how many instances are in front of them.

### Additional Scoping
Using a unique plugin namespace along with a deterministic device ID is enough to
ensure globally unique IDs within a deployment. If desired, additional components may be attached
to the plugin namespace to make IDs unique across a greater scope, e.g. a cluster's deployment
name (assuming a constant deployment name).

### Implementation
All device ID generation happens at the plugin level. As mentioned earlier in the doc,
there are no significant change to how device IDs are generated within the plugin scope.

> We could still look for better ways of doing device ID generation, but it is not a requirement
> for Synse v3.

Based on the different use cases listed above, the plugin will need to be configured for its
appropriate deployment. The default should be case 2 (single instance, scheduled anywhere) and
should use the plugin name.

In addition to setting the deployment strategy of the plugin, the configuration will support
augmenting the plugin namespace with additional prefixes (e.g. cluster ID).

#### Config
Note: The `namespace` configuration is optional, though it is highly recommended to explicitly
set it for each plugin. If the `namespace` section does not exist, the plugin will use the default
behavior for the *single*-type plugin namespace (e.g. using the plugin *tag* -- see below for more info).

**Example**
```yaml
# config.yaml

namespace:
  type: single
  prefix:
  - value: foobar
  - env: FOOBAR
```

##### `namespace`
*namespace* is a new section in the plugin config that contains all of the info for
the plugin ID namespace.

##### `type`
The *type* of the namespace for the plugin. This is determined by the plugin deployment
strategy. Any value specified for the *type* field other than those specified
below will result in a config error. The valid values are:

- host
- single
- multi

**host**

The plugin is host-bound (Kubernetes DaemonSet, run directly on host machine, ...)

The default behavior for *host*-type plugins is to use the machine-id as the base namespace
for the plugin. For example, on linux machines, it will look in `/var/lib/dbus/machine-id`
or `/etc/machine-id` to get the value.

When running in a docker container, the host's machine ID will not be available, so it would
need to be volume mounted. Using the machine ID may not always be desirable, so a secondary option
is available: an environment variable may be used. 

*Examples*

```yaml
# default behavior: look up machine id

namespace:
  type: host
``` 

```yaml
# use non-default file (e.g. if volume mounting somewhere that is not on the
# default search path)

namespace:
  type:
    host:
      file: /tmp/machine-id
```

```yaml
# use a value specified by environment variable instead of looking up machine
# id from file

namespace:
  type:
    host:
      env: HOST_NAME
```


**single**

The plugin can be scheduled anywhere; only a single instance of the plugin is run.

The default behavior for *single*-type plugins is to use the plugin *tag* (a normalized string
combining the plugin name and maintainer metainfo, e.g. "maintainer/plugin-name") as the
base namespace for the plugin. For example, Vapor's IPMI plugin would use the tag "vaporio/ipmi-plugin".

This information is set by the plugin (e.g. see: the [Emulator Plugin](https://github.com/vapor-ware/synse-emulator-plugin/blob/8abac25404d5c341f55441b418f9fc88a8e6fdcc/main.go#L10-L24))
and is always available to the plugin.

*Examples*

```yaml
# default behavior: use plugin tag

namespace:
  type: single
```

```yaml
# Use a hardcoded value instead of the plugin tag

namespace:
  type:
    single:
      value: foobar
```

```yaml
# Use a value specified by environment variable instead of using the plugin tag

namespace:
  type:
    single:
      env: PLUGIN_ID_NAMESPACE
```

**multi**

The plugin can be scheduled anywhere; multiple instances of the plugin can be running.

**TODO**


##### `prefix`
The *prefix* section is optional and allows users to specify any additional prefixes that will
be prepended to the plugin ID namespace. If multiple prefixes are specified, they are prepended
onto the plugin namespace in the order that they are listed.

Prefixes can be specified in different ways:

- `value`: Use the specified value as a prefix component. No processing is done on the value.
- `env`: Get the prefix component from the specified environment variable.