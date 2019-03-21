# Appendix B
Synse v3 appendix for changes to the SDK.


## ~~OutputTypes~~
> **REMOVED** : This section is removed from the spec. See [Amendment 2](amendment-2.md).

~~To remove the need to manually define all OutputTypes and simplify the device
configuration to not require them, the SDK will have a bunch of common outputs
pre-defined:~~

```

var OutputTemperature = OutputType {
  ...
}

var OutputVoltage = OutputType {
  ...
}

var OutputAirflow = OutputType {
  ...
}

var OutputHumidity = OutputType {
  ...
}

```

~~These outputs are considered default and will be automatically registered
to the plugin on init via the SDK. The plugin author will have access to
all of these types.~~

~~A plugin can also define its own custom outputs~~

```

var CustomMemory = sdk.OutputType {
  ...
}

```

~~Custom output types will also be registered with the plugin
as part of the plugin setup.~~


~~Similar to today, these output types will be used to generate the
reading responses for device reads. There are two ways that the output types
can be used, which stems from the two general use cases for device handlers:~~

* ~~Device-specific handler~~
  * ~~An example of a device-specific handler would be an MAX11610 Temperature sensor
    handler for I2C, e.g. This handler would only work with those devices.~~
* ~~Generalized handler~~
  * ~~An example of a generalized handler would be the Modbus-IP plugin's "coils" or
    "register" handler. It is not designed to work for any one specific device, but
    for any device that speaks Modbus-IP.~~


~~For a device-specific handler, the configuration is generally simpler since you know
what the device is and what it can return. In these cases, the output type can just
be imported and used directly, e.g.~~

```
import "github.com/vapor-ware/synse-sdk/sdk/outputs

func read() {
    ...
    
    outputs.Temperature.DoSomething()
}
```

~~When dealing with a generalized handler, we will know what the output type is for
the reading by default. In the case of Modbus-IP, it is just some data that we get
from some register. We need to add configuration to tell the plugin what that data
represents. In this case, we'll need to specify in the configuration which output
type to use. This will be done by a named lookup for registered output types.~~

~~There is no restriction on output type naming, other than they can not collide.
The default outputs will have simple names (e.g. "temperature", "humidity", ...),
so if a custom output is defined, it can not override any of those names. It can
be differentiated in any manner (e.g. 'custom-temperature', 'custom.temperature', 
'temperature2'), though we should standardize on a naming convention (probably
dot notation, since that has been used in previous SDK versions).~~

~~(pseudo-config)~~
```yaml

- name: foo
  output: temperature

```

> ~~NOTE: A limitation on the generalized handlers is that we can't really specify
> multiple outputs for a single 'device' (e.x. register). If we had multiple readings
> from a single register and had to specify multiple output types, it is unclear how
> we would be able to reliably know which reading belongs to which output type.~~


## ~~System of Measure~~
> **REMOVED** : This section is removed from the spec. See [Amendment 2](amendment-2.md).

~~Not all devices will provide data in the same System of Measure (SoM) (e.g. imperial or metric),
and different users may want to retrieve data in a different SoM. In order to provide flexibility
and to be able to have a standard output, OutputTypes should define a SoM and means of converting
between different SoMs. Realistically, we will only need to support imperial (U.S.) and metric, but
the implementation should remain flexible to make it easy to add in other systems in the future.~~

~~(pseudo-code)~~
```
type OutputType struct {
  // The name of the output type
  Name string
  
  // The native system of measure that is used for the
  // device reading. E.g. if a MAX11610 device returns
  // its data in °C, this would be "metric".
  SystemOfMeasure string

  Conversions []UnitConversion
}


// this would likely be called internally and not something the plugin implementer
// would need to worry about, since the SDK should know the context we are operating
// under, so it should know which system of measure we want to use.
func (output *OutputType) Convert(system string, value interface{}) (...) {
  for c := range output.Conversions {
    if output.SystemOfMeasure == system {
      return c.Convert(system, value)
    }
  }
  return error
}



// Example conversions:

UnitConversion {
  Name: "metric",
  Convert: func(system string, value interface{}) (interface{}, Unit, error) {
      switch system:
      case "metric":
          // no conversion
          return value, Celsius{}, nil
      case "imperial":
          // convert from C -> F
          return fahrenheitValue, Fahrenheit{}, nil
      default:
          error (unsupported system)
  }
}

UnitConversion {
  Name: "imperial",
  Convert: func(system string, value interface{}) (interface{}, Unit, error) {
      switch system:
      case "metric":
          // convert from F -> C
          return celsiusValue, Celsius{}, nil
      case "imperial":
          // no conversion
          return value, Fahrenheit{}, nil
      default:
          error (unsupported system)
  }
}
```

## Contexts
In order to ~~know what the requested system of measure is, and to~~ make it easier to pass other
data to a read handler, the read (and bulk read, and likely listen) functions should be updated
to also accept a Context, e.g.

(pseudo-code)
```
type DeviceHandler struct {
  Read     func(*Context, *Device)
  BulkRead func(*Context, []*Device)
  Listen   func(*Context, *Device, chan *ReadContext)
}
```

~~Where the `Context` would at least define the System of Measure for the request. It could
contain more.~~ Having this would also provide a way to pass other data to the handlers
more easily, should that be needed.

> *Note*: There will likely need to be a bit of renaming of things. We currently have a
> `PluginContext` (global context for the plugin) and a `ReadContext` (context around a bunch
> of reading responses), so adding a `Context` on top of that could get confusing. I think
> ideally, `ReadContext` would get renamed to something else (ReadBlock, ReadGroup, MultiReading,
> Readings, ...), and the new `Context` could be called `ReadContext` (since it is the context
> that is passed in to the Read functions) or simply just remain as `Context`.


## Configuration
The plugin and device configuration require some changes and could be simplified in a number
of ways. 

### Plugin Config
Below is a fully filled out Plugin config as per Synse v2. Some of the values are arbitrarily
set just to showcase all possible options.

```yaml
version: 3
debug: true
network:
  type: tcp
  address: ":5001"
  tls:
    cert: "path/to/cert"
    key: "path/to/key"
    caCerts:
      - "list/of/ca/certs"
    skipVerify: false 
settings:
  mode: parallel
  listen:
    enabled: true
    buffer: 100
  read:
    enabled: true
    interval: 1s
    buffer: 100
    serialReadInterval: 0s
  write:
    enabled: true
    interval: 1s
    buffer: 100
    max: 100
  transaction:
    ttl: 5m
  cache:
    enabled: false
    ttl: 3m
limiter:
  rate: 0
  burst: 0
health:
  useDefaults: true
dynamicRegistration:
  config: {} # arbitrary map
context: {}  # arbitrary map
```

For the most part, the only changes that could be made are renaming things to be more clear
or more generalized. For example:
- `settings.read.serialReadInterval` could be generalized so it does not just pertain to
  serial reads.
- `settings.read.interval` and `settings.read.serialReadInterval` could be renamed so it
  is clearer what each option refers to.
- `settings.write.max` could be renamed to `settings.write.batchSize` or something similar
  to more clearly designate it is the number of writes to execute in one pass.
- `settings.cache` could be renamed to `settings.readingsCache`
- `health.useDefaults` could be renamed to make it more clear that it enables/disables the
  built-in health checks for the plugin.

Other fields will need to be added:

- The health check configuration will need to be expanded to something like:
  ```yaml
  health:
    healthFile: /etc/synse/healthy
    checks:
      enableDefaults: true
  ```

There may also need to be configuration options for enabling/disabling metrics, but that
is still TBD.


### Device Kind v. Device Type
The distinction between device type and device kind is confusing and can be simplified. In
fact, the device kind is likely not needed any more. Currently, the device kind is used for
two purposes:

* matching the device with its handler (unless the `handler` field is also specified)
* getting the device type from the last namespaced element

By removing device kind, we can just use the `handler` field to specify which DeviceHandler
it should use.


Before examining other changes, below is the current structure for device configurations.

```
type DeviceConfig struct {
	SchemeVersion
	Locations     []*LocationConfig
	Devices       []*DeviceKind
}

type DeviceKind struct {
	Name         string
	Metadata     map[string]string
	Instances    []*DeviceInstance
	Outputs      []*DeviceOutput
	HandlerName  string
}

type DeviceInstance struct {
	Info                     string
	Location                 string
	Data                     map[string]interface{}
	Outputs                  []*DeviceOutput
	DisableOutputInheritance bool
	SortOrdinal              int32
	HandlerName              string
}

type DeviceOutput struct {
	Type  string
	Info  string
	Data  map[string]interface{}
}
```

Below are some notes and possible changes:
* `DeviceKind.Name` is removed, as it is not needed and only causes confusion.
* `DeviceKind.HandlerName` can be renamed to just `DeviceKind.Handler`
* `Locations` gets replaced with `Tags`, allowing custom tags to be defined.
  * `Tags` fields are added to the `DeviceKind` struct and `DeviceInstance` struct
* The `DeviceKind` struct could be renamed to `DevicePrototype` to be a bit more clear
  on what it is (since "kind" isn't really clear on that).
* The `Config` suffix could be added to these structs to make the distinction more clear
  on what is a configuration object and what is an internal model object.
* `Type` could be added to `DeviceKind`. Its unclear whether it would serve a purpose
  in the SDK, but would at the very least just be metadata on the device for upstream
  consumers, making it easier for them to identify and use. There are no restrictions
  on what the type value can be.
* `DeviceInstance.SortOrdinal` could be renamed to `DeviceInstance.SortIndex` to make
  its intended usage a bit more clear. Not necessary; just a thought.
* `*.Outputs` does not cause any kind of validation errors nor is it required for the
  device to be able to get its output. It can still be specified so that the upstream
  consumer of the API knows what outputs belong to which devices. The config here only
  supplies that metainfo, it isn't required for any internal processing.



Based on the above, the internal modeling for devices and outputs could change as well.
Currently, we have:

```
type Device struct {
	Kind        string
	Metadata    map[string]string
	Plugin      string
	Info        string
	Location    *Location
	Data        map[string]interface{}
	Outputs     []*Output
	Handler     *DeviceHandler
	id          string
	bulkRead    bool
	SortOrdinal int32
}

type Output struct {
    Name          string
    Precision     int
    Unit          Unit
    ScalingFactor string
    Conversion    string
    Info          string
    Data          map[string]interface{}
}
```

With the changes mentioned above, this could look something like:
```
type Device struct {
  Type      string
  Metadata  map[string]string
  Info      string
  Tags      []Tag
  Data      map[string]interface{}
  Handler   *DeviceHandler
  SortIndex int32
  
  id       string
  bulkRead bool
}

type Output struct {
    Name          string
    Precision     int
    Unit          Unit
    ScalingFactor string
    Info          string
    Data          map[string]interface{}
}
```

* `Device.Plugin` is removed. This information is available internally and does not need to be
  part of the device model. All Devices defined within a plugin will belong to that plugin
  so while we may want to know this upstream, we don't need to know it within the SDK.
* `Device.Outputs` are removed. We shouldn't need to specify the outputs for a device. It
  can just get import them and use them as necessary.
* `Output.Conversion` is removed, since that will be baked in to the type definition and won't
  need to be configured.
  
  
> Note: ScalingFactor may be able to move out of the Output definition and into a Config
> definition somewhere. The Outputs should more or less be generic (we don't want to mandate
> something like a TimeMsToS type which applies the scaling factor to get the raw data in ms
> to s when we already have a Seconds type). If in the config, we could use the seconds type
> and just apply the transformation of the raw value prior to building a reading off of that
> output type...