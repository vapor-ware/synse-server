[![CircleCI](https://circleci.com/gh/vapor-ware/synse-server.svg?style=shield)](https://circleci.com/gh/vapor-ware/synse-server)
<img src="https://github.com/vapor-ware/synse-server/raw/master/assets/logo.png" width=25% align=right>

# Synse Server

## Overview

Synse Server provides a JSON API for monitoring and control of data center and IT
equipment, including reading sensors and server power control - via. numerous
backend protocols such as IPMI, Redfish, SNMP, I2C, RS485, and PLC. The API is
easy to integrate into third-party monitoring, management and orchestration
providers. It provides a simple, curl-able interface for common and custom
devops tasks.

The [CLI](cli) makes it even easier to see what's going on with your physical
hardware. You can use it to do any kind of scripting required for your use cases.

The Synse Server API can be consumed via GraphQL with [synse-graphql](grapql). 

If you're looking for an integration, check out [synse-prometheus](prometheus).
You'll be able to put together complete monitoring and dashboard solution from
the instructions there.

Additional documentation may be found on the [Docs][docs] site.

## Getting Started

## Running Synse Server

There are a variety of options on how Synse Server can be run:
 - on [Ubuntu 16.06](#ubuntu-1604)
 - on [CentOS 7](#centos-7)
 - via [Docker](#docker)


### Ubuntu 16.04

1. Get the software.

    ```
    curl -s https://packagecloud.io/install/repositories/VaporIO/synse/script.deb.sh | sudo bash
    sudo apt-get install synse-server
    ```

    > Note that if you'd like more detailed instructions, you can see [package cloud](pkg-cloud).

2. Edit the configuration file. Note, if you'd like to kick the tires and don't
have hardware sitting around, it is possible to [run an emulator](#emulators) that
mocks out the data.

    ```
    vi /etc/synse-server/config.json
    ```

3. Startup the server.

    ```
    sudo systemctl start synse-server
    ```

4. Verify that everything is up and running by issuing a 'scan' command. The
response should be all your configured servers.

    ```
    curl http://localhost:5000/synse/1.4/scan
    ```

### CentOS 7

1. Get the software.
    ```
    curl -s https://packagecloud.io/install/repositories/VaporIO/synse/script.rpm.sh | sudo bash
    sudo yum install synse-server
    ```

    > Note that if you'd like more detailed instructions, you can see [package cloud](pkg-cloud)

2. Edit the configuration file. Note, if you'd like to kick the tires and don't
have hardware sitting around, it is possible to [run an emulator](#emulators) that
mocks out the data.

    ```
    vi /etc/synse-server/config.json
    ```

3. Startup the server.

    ```
    sudo systemctl start synse-server
    ```

4. Verify that everything's up and running by issuing a 'scan' command. The
response should be all your configured servers.

    ```
    curl http://localhost:5000/synse/1.4/scan
    ```

### Docker

1. Create a configuration file. There are multiple examples in the repo under the
`configs/synse` directory. The [documentation][docs] has more details on what can
be configured. Note, if you'd like to kick the tires and don't have hardware sitting
around, it is possible to [run an emulator](#emulators) that mocks out the data.

2. Run the container

    ```
    docker run -p 5000:5000 -v config.json:/synse/config.json vaporio/synse-server
    ```

4. Verify that everything's up and running by issuing a 'scan' command. The
response should be all your configured servers.

    ```
    curl http://localhost:5000/synse/1.4/scan
    ```

## Building an Synse Server Image

To build a custom distribution of Synse (for example, to include site-specific
TLS certificates, or to configure Nginx to use site-specific authn/authz), the
included Makefile can be used to package up the distribution.

In the simplest case, from the Synse directory:
```
make build
```

## Emulators

To use Synse with data available, you can run it with an emulator for a given protocol.
LAN-based protocols (IPMI, Redfish, and SNMP) use an external Docker container to
run the emulator, while serial-based protocols (PLC, I2C, RS485) each have an emulator
that can run in parallel with Synse inside the Synse container. See the full
[documentation][docs] for more.

Starting with a PLC emulator can be done simply with:

```
docker run \
    -p 5000:5000 \
    -v `pwd`/sample/config_plc.json:/synse/override/config.json \
    vaporio/synse-server emulate-plc
```

For a full accounting of Synse's supported sub-commands, run Synse with the help flag:
```
docker run vaporio/synse-server --help
```

## Tests

The tests for Synse exist in the `synse/tests` directory. The Synse [documentation][docs]
goes into more detail on the test setup.

All tests are containerized for consistency and ease of deployment and integration.
There are many test cases, so running the full suite of tests may take some time.


## Logs

Logs for Nginx, uWSGI, and the Synse Flask application are routed to stdout/stderr of the
container, so they are all viewable via `docker logs`. Logs for a given component are prefaced
with the name of that component, e.g. for Nginx, `nginx  |` - this makes it 
easier to see the logs for the components individually. Where `docker logs synse` (assuming the
container is named `synse`) would get logs for everything, 
- `docker logs synse | grep "synse  |"` would give logs for the Synse Flask application
- `docker logs synse | grep "nginx  |"` would give logs for Nginx
- `docker logs synse | grep "uwsgi  |"` would give logs for uWSGI

## License
Synse is released under GPLv2 - see [LICENSE](license) for more information.


### Troubleshooting

#### Unable to access docker image.
- Workaround is docker login, even if logged in already.


[cli]: https://github.com/vapor-ware/synse-cli
[docs]: http://synse-server.readthedocs.io/en/stable/
[license]: https://github.com/vapor-ware/synse-server/blob/master/LICENSE
[pkg-cloud]: https://packagecloud.io/VaporIO/synse/install
[prometheus]: https://github.com/vapor-ware/synse-prometheus
[graphql]: https://github.com/vapor-ware/synse-graphql
