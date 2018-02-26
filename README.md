<p align="center"><img src="assets/logo.png" width="360"></p>
<p align="center">
    <a href="https://circleci.com/gh/vapor-ware/synse-server"><img src="https://circleci.com/gh/vapor-ware/synse-server.svg?style=shield"></a>
        
<h1 align="center">Synse Server</h1>
</p>

<p align="center">An HTTP API for the monitoring and control of physical and virtual devices.</p>


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
TODO - how to specify user defined configs, default location, how to override via env (SYNSE_CONFIG)

Synse Server has three sources of configuration:
1. Built-in defaults
2. User defined config YAMLs
3. Environment variables

In the list above, each configuration mode takes precedence over the option above it.

As displayed in the [Getting Started](#getting-started) section, the default configurations
can be enough to get Synse Server minimally running.

When configuring Synse Server for your own use, you will at the very least need to configure
the plugins for Synse Server to interface with. Synse Plugins interface with Synse Server via an
[internal gRPC API][synse-grpc]. Server and plugins support using TCP or UNIX socket as the
network protocol for [gRPC][grpc]. In general, TCP is preferred, but there are cases where a UNIX socket
may make more sense. 

By default, there are no plugins configured to run with Synse Server, it is up to the user
to specify which plugins to interface with, and how to interface with them. There are two ways
of doing this for TCP-configured plugins, and three ways for UNIX socket configured plugins.

> **Note**
>
> While there is a distinction between "TCP Plugins" and "Unix Socket Plugins", it is important
> to note that the distinction is at a configuration level. That is to say, all plugins that use
> the SDK have the capability of either being configured for TCP or Unix Socket, not that there
> is one version of a plugin that uses TCP and separate one that uses Unix Sockets.

### Communication Modes
#### TCP
If a plugin is configured for TCP in Synse Server, it should also be configured for TCP in the
plugin configuration. See the [SDK documentation][synse-sdk] for more info on plugin configuration.

There are two ways of configuring a TCP plugin with Synse Server:
 1. By config file
 2. By environment variable
 
To configure **by config file**, you will need to specify the name of the plugin and the 
host/port of the plugin under the `plugin.tcp` field of the configuration. As an example,
for a plugin named "foobar" that is listening on 10.10.1.8:5001, the configuration would
look like
```yaml
plugin:
  tcp:
    foobar: 10.10.1.8:5001
```

To configure **by environment variable**, you will need to specify an environment variable
with the `SYNSE_` prefix followed by the configuration path, followed by the plugin name. The
value of the environment variable should be the host/port of the plugin. As an example, for a 
plugin named "foobar" that is listening on 10.10.1.8:5001, the environment variable would
look like:
```
SYNSE_PLUGIN_TCP_FOOBAR = 10.10.1.8:5001
```

#### Unix Socket
If a plugin is configured for Unix sockets in Synse Server, it should also be configured for Unix
sockets in the plugin configuration. See the [SDK documentation][synse-sdk] for more info on plugin
configuration.

There are three ways of configuring a Unix socket plugin with Synse Server:
 1. By config file
 2. By environment variable
 3. By using the default socket path
 
To configure **by config file**, you will need to specify the name of the plugin and the 
directory where the socket exists. The socket is expected to have the same name as the plugin.
This is specified under the `plugin.unix` field of the configuration. As an example,
for a plugin named "foobar" whose socket, "foobar.sock", is in the directory "/tmp/run", the
configuration would look like
```yaml
plugin:
  unix:
    foobar: /tmp/run
```

To configure **by environment variable**, you will need to specify an environment variable
with the `SYNSE_` prefix followed by the configuration path, followed by the plugin name. The
value of the environment variable should be the directory containing the socket for the plugin.
As an example, for a plugin named "foobar" whose socket, "foobar.sock", is in the directory 
"/tmp/run", the environment variable would look like:
```
SYNSE_PLUGIN_UNIX_FOOBAR = /tmp/run
```

To configure **by using the default socket path**, then all you will have to do is put the socket
file into the default socket path for Synse Server (Note: if running Synse Server in a container,
this means volume mounting). The default path is `/tmp/synse/procs`, so if you had a plugin named
"foobar" whose socket, "foobar.sock" was in "/tmp/synse/procs", then you would not need to specify
anything in the YAML configuration or via environment variable. 

While its not necessary to specify anything in this case, it is often still good practice to
list it in the configuration. If there is a plugin whose socket exists in the default location
and you want to include it in the config for visibility, you can do so and omit the socket path - 
this tell Synse Server to look for it in the default location.
```yaml
plugin:
  unix:
    foobar:
```

### Default Configuration
The default configuration is as follows:
```yaml
locale: en_US
pretty_json: false
logging: info
cache:
  meta:
    ttl: 20
  transaction:
    ttl: 20
grpc:
  timeout: 3
```

### Configuration Options

### Full Example Configuration
Below is a valid complete example of a configuration file.
```yaml
logging: debug
pretty_json: true
locale: en_US
plugin:
  tcp:
    emulator: localhost:6000
    plugin1: 54.53.52.51:5555
  unix:
    # a unix socket named 'plugin2' found in the default location
    plugin2:
    # a unix socket named 'plugin3' found in /tmp/run
    plugin3: /tmp/run
cache:
  meta: 
    ttl: 20
  transaction:
    ttl: 20
grpc:
  timeout: 5
```

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
To develop Synse Server, you will first need to clone this repo
```
git clone https://github.com/vapor-ware/synse-server.git
cd synse-server
```

All work should be done in branches and pull requests made to merge the branch
back into master. For work to make its way back into master, it must pass the CI
checks (building, testing, linting).

The Makefile contains a bunch of targets that are useful for development. For more, see the
[Makefile](Makefile), or use `make help` to list and describe the available targets.

Testing and linting are done using [tox][tox]. If Python 3.6 is installed locally, testing
and linting will run locally. Otherwise, they will be executed in a docker container where
Python 3.6 is available.

### Building
The Synse Server Docker image can be built locally with 
```
make docker
```
It will build [release.dockerfile](dockerfile/release.dockerfile) and tag it with 'latest', 
the current git hash, and the current version of Synse Server.

### Testing
There are three types of tests that can be run:

Unit tests:
```
make test-unit
```

Integration tests:
```
make test-integration
```

End-to-end tests:
```
make test-end-to-end
```

All tests can be run consecutively with `make test`.

To get a coverage report from the previous test run, see the generated `results/cov-html/index.html`,
or you can run `make cover` to run the unit tests and open the resulting coverage report.

### Linting
Synse Server source code and test code is linted with isort and pylint to keep it clean and consistent.
```
make lint
```

## License
Synse is released under GPLv2 - see [LICENSE](LICENSE) for more information.


[docs]: http://opendcre.com
[cli]: https://github.com/vapor-ware/synse-cli
[prometheus]: https://github.com/vapor-ware/synse-prometheus
[graphql]: https://github.com/vapor-ware/synse-graphql
[synse-dockerhub]: https://hub.docker.com/r/vaporio/synse-server/
[synse-emulator]: https://github.com/vapor-ware/synse-emulator-plugin
[synse-grpc]: https://github.com/vapor-ware/synse-server-grpc
[synse-sdk]: https://github.com/vapor-ware/synse-sdk
[example-deployment]: https://github.com/vapor-ware/synse-emulator-plugin/tree/master/deploy/docker

[tox]: https://tox.readthedocs.io/en/latest/
[grpc]: https://grpc.io/