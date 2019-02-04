# Appendix A
Synse v3 appendix for configuration examples.

## 1. SDK Device Configurations

### 1.1 I2C Plugin
> *Note: The tags used in the following example are arbitrary and only
> serve as an example for the tag field(s) in the config scheme.

```yaml
version: 2
tags: # optional: global plugin tags (applies to all devices)
- "plugin:i2c"
devices:
- handler: pca9632
  type: led
  metadata:
    model: PCA9632
    manufacturer: NXP Semiconductors
  tags: # optional: prototype tag (applies to the following instances)
  - "vapor/device:led"
  instances:
  - info: Rack LED
    tags: # optional: instance tag (applies to only this device)
    - "vapor/foo:bar"
    data:
      channel: "0014"
```

### 1.2 Modbus TCP/IP Plugin
> *Note: The tags used in the following example are arbitrary and only
> serve as an example for the tag field(s) in the config scheme.

```yaml
version: 2
tags: # optional: global plugin tags (applies to all devices)
- "plugin:modbus-ip"
devices:
- handler: input_register
  type: power
  metadata:
    manufacturer: eGauge
  tags: # optional: prototype tag (applies to the following instances)
  - "vapor/device:power"
  instances:
  - info: eGauge Power Meter
    tags: # optional: instance tag (applies to only this device)
    - "vapor/foo:bar"
    data:
      host: 127.0.0.1
      port: 502
    # This following stays the same. We will want to specify the type
    # information here so the handler knows which type to use for responses.
    # This needs to be set upfront since different registers could provide
    # readings for different sensors.
    outputs:
    - info: L1 to Neutral RMS Voltage
      # This 'type' is different than the device type. It is the type of the
      # output. This needs to match to an existing output type.
      # TODO: consider how this fits in with an output model that accounts
      # for things like unit conversion (imperial, metric)
      type: voltage
      data:
        address: 500
        width: 2
        type: f32
```

### 1.3 IPMI Plugin
The IPMI plugin is a plugin which does not have device configurations. Instead, it uses
dynamic registration to enumerate devices at runtime.

> *Open Question*: What does this mean for assigning custom tags?

### 1.4 SNMP Plugin
The SNMP plugin is a plugin which does not have device configurations. Instead, it uses
dynamic registration to enumerate devices at runtime.

> *Open Question*: What does this mean for assigning custom tags?

### 1.5 sFlow Plugin
> *Note: The tags used in the following example are arbitrary and only
> serve as an example for the tag field(s) in the config scheme.
>
> This plugin is also in early-alpha so the configuration requirements
> for its devices may change.

```yaml
version: 2
tags: # optional: global plugin tags (applies to all devices)
- "plugin:sflow"
devices:
- handler: collector
  metadata:
    protocol: sflow
  tags: # optional: prototype tag (applies to the following instances)
  - "vapor/device:something"
  instances:
  - info: Generic sFlow Collector
    tags: # optional: instance tag (applies to only this device)
    - "vapor/foo:bar"
    data:
      address: "0.0.0.0"
      port: 6343
```

