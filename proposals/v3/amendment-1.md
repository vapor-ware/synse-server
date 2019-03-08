# Amendment 1: Device FQDN & Aliases
Device FQDN is a feature we wish to support in Synse v3. The core requirement of this
feature is for devices in Synse to be uniquely addressable through a stable identifier.
This means that we can reach the device at the same address regardless of whether it is
added, removed, temporarily becomes unavailable, etc.

To fulfill the bare requirements, the [`/device`](api.md#device) endpoint was added,
allowing you to read from a write to a device at a stable address.

```
GET  $host/v3/device/1be67a887c73100927be276d
POST $host/v3/device/1be67a887c73100927be276d
```

With this, some kind of higher level routing/DNS mapping would be able to map an
arbitrary name to the device for reading and writing.

To make things a bit simpler and more extensible, we can allow for aliases to be
defined for devices. These aliases can be defined within the device config. They
should be unique to the device, but it is up to the configurer to ensure their
uniqueness. If a plugin detects that aliases overlap, it can raise an error. If
Synse Server detects that there are overlapping aliases (e.g. if they are across
multiple plugins), it can return an error for any action using that alias.

> **Question**: Should we allow for multiple aliases for a single device?
> We could do it, but it does add complexity to some aspects of data modeling,
> and it widens the search space for device routing.

A device alias can be used anywhere where a device GUID can be used.

```
GET  $host/v3/info/fqdn.device.alias
GET  $host/v3/device/fqdn.device.alias
GET  $host/v3/read?tag=id:fqdn.device.alias
```

The gRPC API would be updated so that device responses would contain an additional
`alias` field. Synse Server's HTTP API would be updated so that `/scan` responses would
also include the alias (could be under the field 'alias' or 'name'), and the `/info`
response would be updated with the same information.


At the SDK level, this would mean that devices could have an additional configuration
field for the alias to be specified. The alias is optional, as a device could always be
referenced by its auto-generated ID if no alias is set for it.

The alias could be defined in one of two ways: defining it directly, or defining a
template for it which the SDK will render.

```yaml
# define the alias directly
alias:
  name: fqdn.device.alias
```

```yaml
# define the alias via template
alias:
  template: {{ .Plugin }}.{{ .DeviceType }}.foo.bar
```

If both a name and template are specified simultaneously, a configuration error is raised.


We will need to define the supported template fields and functions. Below are some
initial thoughts:

| Field | Description |
| :---- | :---------- |
| `{{.Plugin}}` | The name of the plugin. |
| `{{.Maintainer}}` | The plugin maintainer. |
| `{{.DeviceType}}` | The device type. |
| `{{.Handler}}` | The device handler name. |


| Function | Description |
| :------- | :---------- |
| `{{env "HOST"}}` | Get the value of the specified environment variable (e.g., `$HOST`). |
| `{{meta "key"}}` | Get the value for the specified key in the metainfo dict for the device. The metainfo is also defined in config, so this is really just a convenience so that you don't have to update multiple fields if something changes. |

More fields/functions can be added.


