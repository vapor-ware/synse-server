[![CircleCI](https://circleci.com/gh/vapor-ware/synse-server.svg?style=shield&circle-token=8b259c633bf9886a9f4330a6b2d1835d12e11126)](https://circleci.com/gh/vapor-ware/synse-server)
<img src="https://github.com/vapor-ware/synse-server/raw/master/assets/logo.png" width=25% align=right>

# Synse Server

## Overview

Synse Server provides an API for monitoring and control of data center and IT
equipment, including reading sensors and server power control - via. numerous
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

## Getting Started

## Running Synse Server

### Ubuntu 16.04

1. Get the software.

    ```
    curl -s https://packagecloud.io/install/repositories/VaporIO/synse/script.deb.sh | sudo bash
    sudo apt-get install synse-server
    ```

    > Note that if you'd like more detailed instructions, you can see [package cloud](pkg-cloud).

2. Edit the configuration file. Note, if you'd like to kick the tires and don't
have hardware sitting around, it is possible to [run an emulator](#emulator) that
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

5. You can check out some queries by directing your browser to `http://localhost:5000/synse/1.4/graphql`.

### CentOS 7

1. Get the software.
    ```
    curl -s https://packagecloud.io/install/repositories/VaporIO/synse/script.rpm.sh | sudo bash
    sudo yum install synse-server
    ```

    > Note that if you'd like more detailed instructions, you can see [package cloud](pkg-cloud)

2. Edit the configuration file. Note, if you'd like to kick the tires and don't
have hardware sitting around, it is possible to [run an emulator](#emulator) that
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

5. You can check out some queries by directing your browser to `http://localhost:5000/synse/1.4/graphql`.

### Docker

1. Create a configuration file. There are multiple examples in the repo under the
`configs/synse` directory. The [documentation][docs] has more details on what can
be configured. Note, if you'd like to kick the tires and don't have hardware sitting
around, it is possible to [run an emulator](#emulator) that mocks out the data.

2. Run the container

    ```
    docker run -p 5000:5000 -v config.json:/etc/synse-server/config.json vaporio/synse-server
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

## GraphQL

GraphQL endpoints are included in synse-server. The GraphQL endpoints run alongside the 
Synse endpoints and are served
from the same app.

## License
Synse is released under GPLv2 - see [LICENSE](license) for more information.


### Troubleshooting

#### Unable to access docker image.
- Workaround is docker login, even if logged in already.


[cli]: https://github.com/vapor-ware/synse-cli
[docs]: http://opendcre.com
[license]: https://github.com/vapor-ware/synse-server/blob/master/LICENSE
[pkg-cloud]: https://packagecloud.io/VaporIO/synse/install
[prometheus]: https://github.com/vapor-ware/synse-prometheus
