<p align="center"><img src="assets/logo.png" width="360"></p>
<p align="center">
    <a href="https://circleci.com/gh/vapor-ware/synse-server"><img src="https://circleci.com/gh/vapor-ware/synse-server.svg?style=shield"></a>
        
<h1 align="center">Synse Server</h1>
</p>

<p align="center">An HTTP API for monitoring and control of physical and virtual devices.</p>


## Overview

Synse Server provides a simple JSON API to monitor and control physical and virtual devices.
It provides a uniform HTTP interface for back-end plugins implementing various protocols,
such as RS485, I2C, and IPMI. The Synse Server API makes it easy to read from and write
to devices, gather device meta-information, and scan for devices across multiple back-ends
through a curl-able interface.

The [CLI][cli] makes it even easier to interact with Synse Server from the command line.

A [GraphQL][graphql] service can be used to wrap the JSON API in a powerful query language
that lets you perform aggregations/operations over multiple devices easily.

If you're looking for an integration, check out [synse-prometheus][prometheus]. You'll be
able to put together complete monitoring and dashboard solution from the instructions there.

Additional documentation may be found on the [Docs][docs] site.

### Architecture
TODO - will need diagrams, will need a description of how plugins work/interface with
Synse Server


## Getting Started
Synse Server is provided as a Docker image to make it easy to setup and deploy. Additionally,
it is released as a Python package that you can install to run locally without Docker or to
integrate into your application as you see fit. Below are the steps to get Synse Server and
run it with its built-in emulator.

### Docker
1. Get the Docker image from [DockerHub][synse-dockerhub]

    ```
    docker pull vaporio/synse-server
    ```
    
1. Run the container with the default configurations, enabling the emulator
    
    ```
    docker run -d \
        -p 5000:5000 \
        --name synse \
        vaporio/synse-server enable-emulator
    ```

1. Verify that Synse Server is up and running and reachable
    
    ```
    $ curl http://localhost:5000/synse/test
    {
      "status": "ok",
      "timestamp": "2018-02-26 16:58:07.844486"
    }
    ```

1. Issue a `scan` command to list all of the devices known to Synse. The devices that
   Synse Server interacts with are made available by the Synse Plugin(s) it is interfacing
   with, which in this case is the [emulator][synse-emulator].
   
    ```
    curl http://localhost:5000/synse/2.0/scan
    ```

### Python Package
TODO


## Configuration
Synse Server 


## Deploying with Plugins
Deploying Synse Server with the emulator is pretty straightforward, as shown in the [Getting Started - Docker](#docker)
section. In practice, running Synse Server with plugins is somewhat more complex because all
other plugins live external to the Synse Server image.

> **Side Note**
> 
> While generally not recommended, you can build a custom Synse Server image that
> includes a plugin binary to have them run in the same container. This is what is done
> with the emulator plugin and is done more out of convenience than necessity.

The [configuration](#configuration) section contains some information on how to register plugins
with Synse Server. The [Synse SDK][synse-sdk] provides information on the configurations needed
at the plugin level. An [example deployment][example-deployment] can be found in the emulator
repository that shows how to run Synse Server with an external emulator container both via
TCP and UNIX socket.

## Development

### Building

### Testing

### Linting


## Contributing


## License
Synse is released under GPLv2 - see [LICENSE](LICENSE) for more information.








## Building
The Synse Server 2.0 Docker image can be built using the make target
```
make build
```


## Testing
Synse Server 2.0 contains unit tests, integration tests and end-to-end tests.
Unit and integration tests can be run with the make target
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

End-to-end tests can be run individually with
```
make etest
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
    - default: `/tmp/synse/procs`
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
Synse is released under GPLv2 - see [LICENSE](LICENSE) for more information.


[docs]: http://opendcre.com
[cli]: https://github.com/vapor-ware/synse-cli
[prometheus]: https://github.com/vapor-ware/synse-prometheus
[graphql]: https://github.com/vapor-ware/synse-graphql
