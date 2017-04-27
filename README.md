<img src="http://www.vapor.io/wp-content/uploads/2015/11/openDCRElogo.png" width=144 height=144 align=right>

# OpenDCRE

## Overview
OpenDCRE provides a securable RESTful API for monitoring and control of data center and IT equipment, including reading sensors and server power control - via power line communications (PLC) over a DC bus bar, via IPMI over LAN, or via Redfish over LAN. The OpenDCRE API is easy to integrate into third-party monitoring, management and orchestration providers, while providing a simple, curl-able interface for common and custom devops tasks.

Additional documentation may be found on the [documentation][docs] site.


## Building an OpenDCRE Image

To build a custom distribution of OpenDCRE (for example, to include site-specific TLS certificates, or to configure Nginx to use site-specific authn/authz), the included Makefile can be used to package up the distribution.

In the simplest case, from the opendcre directory:

```
make build
```

## Running OpenDCRE

```
make run
```

This starts up OpenDCRE and an emulated IPMI environment so that you can play around. Point your browser at http://<my-host>:5000/opendcre/1.3/graphql for an interactive environment that lets you query the system. Alternatively, you can `curl http://localhost:5000/opendcre/1.3/scan` or read the [documentation][docs].

## Tests

The tests for OpenDCRE exist in the `opendcre_southbound/tests` directory. The OpenDCRE documentation goes into more detail on the test setup.

All tests are containerized for consistency and ease of deployment and integration. There are many test cases, so running the full suite of tests may take some time.

## Emulators

To use OpenDCRE with data available, you can run it with the PLC emulator (IPMI and Redfish emulators exist as well, see the full documentation for more). With the OpenDCRE image built, this can be done with:

```
docker run \
    -p 5000:5000 \
    -v `pwd`/sample/config_plc.json:/opendcre/override/config.json \
    vaporio/opendcre ./start_opendcre_plc_emulator.sh
```

## GraphQL

GraphQL endpoints are included in synse-server and can be found in the `graphql` subdirectory. The GraphQL endpoints
run alongside the Synse endpoints and are served from the same port.

### Kick the tires

Note: the default configuration uses `demo.vapor.io`. If you'd like to use a different backend, check out `--help`.

#### From the web

    make run

At this point there is an interactive terminal running that you can do interactive queries with. Send your browser to 
`http://localhost:5001/graphql` and play around. Click the `Docs` tab on the right for the schema or go to 
`tests/queries/` to look at some example queries.

#### From the command line

    make dev
    python runserver.py &
    ./bin/query --list
    ./bin/query test_racks
    ./bin/query --help

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
