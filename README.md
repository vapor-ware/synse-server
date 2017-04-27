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

## License
OpenDCRE is released under GPLv2 - see LICENSE for more information.

[docs]: http://opendcre.com
