![logo](https://github.com/vapor-ware/synse-server/raw/master/assets/logo.png)

# Synse Server

## Overview

Synse Server provides an API for monitoring and control of data center and IT equipment, including reading sensors and server power control - via. IPMI over LAN or Redfish over LAN. The API is easy to integrate into third-party monitoring, management and orchestration providers. It provides a simple, curl-able interface for common and custom devops tasks.

The [CLI](https://github.com/vapor-ware/synse-cli) makes it even easier to see what's going on with your physical hardware. You can use it to do any kind of scripting required for your use cases.

If you're looking for an integration, check out [synse-prometheus](https://github.com/vapor-ware/synse-prometheus). You'll be able to put together complete monitoring and dashboard solution from the instructions there.

Additional documentation may be found on the [Docs][docs] site.

## Getting Started

## Running Synse Server

### Ubuntu 16.04

1. Get the software.

```
curl -s https://packagecloud.io/install/repositories/VaporIO/synse/script.deb.sh | sudo bash
sudo apt-get install synse-server
```

    Note that if you'd like more detailed instructions, you can see [package cloud](https://packagecloud.io/VaporIO/synse/install)

1. Edit the configuration file. Note, if you'd like to kick the tires and don't have hardware sitting around, it is possible to [run an emulator](#emulator) that mocks out the data.

```
vi /etc/synse-server/config.json
```

1. Startup the server.

```
sudo systemctl start synse-server
```

1. Verify that everything's up and running. The response should be all your configured servers.

```
curl http://localhost:5000/synse/1.4/scan
```

1. You can check out some queries by directing your browser to `http://localhost:5000/synse/1.4/graphql`.

### CentOS 7

1. Get the software.

```
curl -s https://packagecloud.io/install/repositories/VaporIO/synse/script.rpm.sh | sudo bash
sudo yum install synse-server
```

    Note that if you'd like more detailed instructions, you can see [package cloud](https://packagecloud.io/VaporIO/synse/install)

1. Edit the configuration file. Note, if you'd like to kick the tires and don't have hardware sitting around, it is possible to [run an emulator](#emulator) that mocks out the data.

```
vi /etc/synse-server/config.json
```

1. Startup the server.

```
sudo systemctl start synse-server
```

1. Verify that everything's up and running. The response should be all your configured servers.

```
curl http://localhost:5000/synse/1.4/scan
```

1. You can check out some queries by directing your browser to `http://localhost:5000/synse/1.4/graphql`.

### Docker

1. Create a configuration file. There is an [example](https://github.com/vapor-ware/synse-server/blob/master/bmc-config.json) in the repo. The [documentation][docs] has details on what else can be configured. Note, if you'd like to kick the tires and don't have hardware sitting around, it is possible to [run an emulator](#emulator) that mocks out the data.

2. Run the container

```
docker run -p 5000:5000 -v config.json:/etc/synse-server/config.json vaporio/synse-server
```

4. Verify that everything's up and running. The response should be all your configured servers.

```
curl http://localhost:5000/synse/1.4/scan
```

## Building an Synse Server Image

To build a custom distribution of Synse (for example, to include site-specific TLS certificates, or to configure Nginx to use site-specific authn/authz), the included Makefile can be used to package up the distribution.

In the simplest case, from the Synse directory:
```
make x64
```

## Emulators

To use OpenDCRE with data available, you can run it with the IPMI emulator (Redfish emulator exists as well, see the full [documentation][docs] for more). This can be done simply with:

```
docker run \
    -p 5000:5000 \
    -v `pwd`/sample/config_plc.json:/opendcre/override/config.json \
    vaporio/opendcre ./start_opendcre_plc_emulator.sh
```

## Tests

The tests for OpenDCRE exist in the `opendcre_southbound/tests` directory. The OpenDCRE documentation goes into more detail on the test setup.

All tests are containerized for consistency and ease of deployment and integration. There are many test cases, so running the full suite of tests may take some time.

## GraphQL

GraphQL endpoints are included in synse-server and can be found in the `graphql` subdirectory. The GraphQL endpoints run alongside the Synse endpoints and are served from the same port.

### Development

#### Run the server

    make dev
    python runserver.py

- From outside the container (or inside it), you can run `curl localhost:5001`

#### Run the tests (as part of development)

1. Run the tests

    make dev
    make one test="-a now"`

See [nosetests](http://nose.readthedocs.io/en/latest/usage.html) for some more examples. Adding `@attr('now')` to
the top of a function is a really convenient way to just run a single test.

#### Getting isort errors?

- See the changes:

    isort graphql_frontend tests -rc -vb --dont-skip=__init_.py --diff

- Atomic updates:

    isort graphql_frontend tests -rc -vb --dont-skip=__init_.py --atomic

### Testing (run the whole suite)

- Tests assume a running, emulated synse-server on the same host. It uses `localhost` to talk to the router. If this
you'd like to use a different synse-server, change the config.
- `make test`

## License
OpenDCRE is released under GPLv2 - see LICENSE for more information.

[docs]: http://opendcre.com
