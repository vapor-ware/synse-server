<img src="https://github.com/vapor-ware/synse-server/raw/master/assets/logo.png" width=25% align=right>

# Synse Server 2.0 *DEV*

NOTE: this is the development branch for synse-server v2.0. the architecture here
is pretty different from the v1.X branches. **this branch is NOT intended to be merged
into master here.** it is just meant to be a source-controlled place for development. 

once it comes time to release v2, what will likely need to happen is this branch will
get copied into the public synse server repo as a branch. that will probably be a bit
of a headache, but once that is done and synse server v2.0 is live, then we will no
longer have to maintain a public and private repo for synse server and life will be 
much simpler.

## Overview

Synse Server provides an API for monitoring and control of data center and IT
equipment, including reading sensors and server power control - via numerous
backend protocols such as IPMI, Redfish, SNMP, I2C, RS485, and PLC. The API is
easy to integrate into third-party monitoring, management and orchestration
providers. It provides a simple, curl-able interface for common and custom
devops tasks.

The [CLI](cli) makes it even easier to see what's going on with your physical
hardware. You can use it to do any kind of scripting required for your use cases.


If you're looking for an integration, check out [synse-prometheus](prometheus).
You'll be able to put together complete monitoring and dashboard solution from
the instructions there.

Additional documentation may be found on the [Docs][docs] site.


## Building
The Synse Server 2.0 Docker image can be built using the make target
```
make build
```


## Testing
Synse Server 2.0 contains both unit and integration tests. Both suites of tests
can be run with the make target
```
make test
```

or they can be run individually.
```
# unit tests
make utest

# integration tests
make itest
```


## Linting
Synse Server 2.0 source code can be linted using the make target
```
make lint
```


## Configuration

### Supports
- Setting defaults.
- Reading from YAML config files.
- Reading from environment variables.
 
### Precedence order
Each item takes precedence over the item below it:
- Environment variables.
- Config files.
- Default options.

### Configuration file
- Only supports YAML for now.
- Default configuration filepath is `/synse/config/config.yml`.

### Configurable options
- `pretty_json`: JSON format's response with indents and spaces
  - type: `bool`
  - default: `False`
  - options: `True | False`
- `logging`: logging level
  - type: `str`
  - default: `info`
  - options: `debug | info | warning | error | critical`
- `plugin`
  - `unix`: UNIX socket location 
    - type: `dict`
    - default: `/synse/procs`
    - options: to be set using `{name}:{path}` format
  - `tcp`: TCP plugin
    - type: `dict`
    - default: not set anywhere
    - options: to be set using `{name}:{address}` format
- `cache`:
  - `ttl`: Time-to-live
    - type: `int`
    - default: `20`
    - options: to be set
- `grpc`:
  - `timeout`: timeout for gRPC calls, including read, write, transaction, metainfo
    - type: `int`
    - default: `20` seconds
    - options: to be set
- `locale`: for translation purpose, can be set to other languages.
    - type: `str`
    - default: `en_US`
    - options: [Localization's documentation](locale/README.md) goes into more details on languages setup.

### Configuration's file example
```YAML
pretty_json: True
logging: debug
plugin:
  unix:
    foo: /synse/example
  tcp:
    bar: localhost:5000
cache:
  ttl: 10
grpc:
  timeout: 10
locale: nl_BE
```

### Setting environment variables
The environment varibles can be set outside the application, 
in whatever environment user is running. 

However, it should follow this format: `SYNSE_{KEY}={VALUE}`, where:
- `SYNSE` is the prefix for our application.
- `{KEY}` can be anything in UPPERCASE.
- `{KEY}` must NOT have a delimiter `_`.

If user want to set a value for a nested key, 
it's almost similar: `SYNSE_{KEY1}_{KEY2}_{KEY3}={VALUE}`, where:
- Each key is separated by a delimiter `_`
- `{KEY1}...{KEYN}` are keys.


### Add a custom configuration filepath using environment variable
This allows users to specify the location of a file they want to use and
not require it to be in the default location.

It should follow the format: `SYNSE_CONFIG={CUSTOM_FILE_PATH}`.

For example: `SYNSE_CONFIG=/tmp/cfg.yml`


## License
Synse is released under GPLv2 - see LICENSE for more information.


[cli]: https://github.com/vapor-ware/synse-cli
[docs]: http://opendcre.com
[license]: https://github.com/vapor-ware/synse-server/blob/master/LICENSE
[prometheus]: https://github.com/vapor-ware/synse-prometheus
