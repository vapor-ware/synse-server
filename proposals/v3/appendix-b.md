# Appendix B
Synse v3 appendix for changes to the SDK.

> **Note**: This appendix is written in a stream-of-thought flow for how various
> aspects of the SDK could be changed/improved. They are just thoughts and should
> be taken as such, with scrutiny placed on them for whether they make sense and
> whether they are useful.


## 1. OutputTypes
To remove the need to manually define all OutputTypes and simplify the device
configuration to not require them, the SDK will have a bunch of common outputs
pre-defined:

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

These outputs are considered default and will be automatically registered
to the plugin on init via the SDK. The plugin author will have access to
all of these types. 

A plugin can also define its own custom outputs

```

var CustomMemory = sdk.OutputType {
  ...
}

```

Custom output types will also be registered with the plugin
as part of the plugin setup.


Similar to today, these output types will be used to generate the
reading responses for device reads. There are two ways that the output types
can be used, which stems from the two general use cases for device handlers:

* Device-specific handler
  * An example of a device-specific handler would be an MAX11610 Temperature sensor
    handler for I2C, e.g. This handler would only work with those devices.
* Generalized handler
  * An example of a generalized handler would be the Modbus-IP plugin's "coils" or
    "register" handler. It is not designed to work for any one specific device, but
    for any device that speaks Modbus-IP.


For a device-specific handler, the configuration is generally simpler since you know
what the device is and what it can return. In these cases, the output type can just
be imported and used directly, e.g.

```
import "github.com/vapor-ware/synse-sdk/sdk/outputs

func read() {
    ...
    
    outputs.Temperature.DoSomething()
}
```

When dealing with a generalized handler, we will know what the output type is for
the reading by default. In the case of Modbus-IP, it is just some data that we get
from some register. We need to add configuration to tell the plugin what that data
represents. In this case, we'll need to specify in the configuration which output
type to use. This will be done by a named lookup for registered output types.

There is no restriction on output type naming, other than they can not collide.
The default outputs will have simple names (e.g. "temperature", "humidity", ...),
so if a custom output is defined, it can not override any of those names. It can
be differentiated in any manner (e.g. 'custom-temperature', 'custom.temperature', 
'temperature2'), though we should standardize on a naming convention (probably
dot notation, since that has been used in previous SDK versions).

(pseudo-config)
```yaml

- name: foo
  output: temperature

```

> NOTE: A limitation on the generalized handlers is that we can't really specify
> multiple outputs for a single 'device' (e.x. register). If we had multiple readings
> from a single register and had to specify multiple output types, it is unclear how
> we would be able to reliably know which reading belongs to which output type.


### System of Measure
Not all devices will provide data in the same System of Measure (SoM) (e.g. imperial or metric),
and different users may want to retrieve data in a different SoM. In order to provide flexibility
and to be able to have a standard output, OutputTypes should define a SoM and means of converting
between different SoMs. Realistically, we will only need to support imperial (U.S.) and metric, but
the implementation should remain flexible to make it easy to add in other systems in the future.

(pseudo-code)
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

### Contexts
In order to know what the requested system of measure is, and to make it easier to pass other
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

Where the `Context` would at least define the System of Measure for the request. It could
contain more. This having this would also provide a way to pass other data to the handlers
more easily, should that be needed.

```
type Context struct {
  SystemOfMeasure string
}
```

> *Note*: There will likely need to be a bit of renaming of things. We currently have a
> `PluginContext` (global context for the plugin) and a `ReadContext` (context around a bunch
> of reading responses), so adding a `Context` on top of that could get confusing. I think
> ideally, `ReadContext` would get renamed to something else (ReadBlock, ReadGroup, MultiReading,
> Readings, ...), and the new `Context` could be called `ReadContext` (since it is the context
> that is passed in to the Read functions) or simply just remain as `Context`.