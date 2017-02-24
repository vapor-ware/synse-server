<img src="http://www.vapor.io/wp-content/uploads/2015/11/openDCRElogo.png" width=144 height=144 align=right>

# OpenDCRE

## Overview
OpenDCRE provides a securable RESTful API for monitoring and control of data center and IT equipment, including reading 
sensors and server power control - via power line communications (PLC) over a DC bus bar, via IPMI over LAN, or via 
Redfish over LAN. The OpenDCRE API is easy to integrate into third-party monitoring, management and orchestration 
providers, while providing a simple, curl-able interface for common and custom devops tasks.

Additional documentation may be found on the <a href="http://opendcre.com">OpenDCRE Read the Docs</a> site.


## Building an OpenDCRE Image
To build a custom distribution of OpenDCRE (for example, to include site-specific TLS certificates, or to 
configure Nginx to use site-specific authn/authz), the included Makefile can be used to package up the distribution.

In the simplest case, from the opendcre directory:
```
make x64
```


## Running and Testing OpenDCRE
OpenDCRE listens for API requests on port 5000 by default. It can run "out of the box", but requires some amount
of configuration to get it communicating with devices (whether emulated or real). To start OpenDCRE out of the box,

```
docker run -d -p 5000:5000 vaporio/opendcre
```

With this, you can hit all endpoints, but since no backend devices are configured, no data will be returned. See the
<a href="http://opendcre.com">OpenDCRE documentation</a> for the API Reference as well as how to properly configure
and run OpenDCRE in "emulated" and "real" modes.

To use OpenDCRE with data available, you can run it with the PLC emulator (IPMI and Redfish emulators exist as well,
see the full documentation for more). With the OpenDCRE image built, this can be done simply with:

```
docker run \
    -p 5000:5000 \
    -v `pwd`/sample/config_plc.json:/opendcre/override/config.json \
    vaporio/opendcre ./start_opendcre_plc_emulator.sh
```

Once it spins up, you can visit the IP address of your Docker instance:

```
http://IPADDRESS:5000/opendcre/1.3/test
```

You should get the response:

```
{
  "status": "ok"
}
```

Other OpenDCRE commands (scan, read, power, etc) should also work and provide responses with emulated data.


The tests for OpenDCRE exist in the `opendcre_southbound/tests` directory. The OpenDCRE documentation goes into more
detail on the test setup, but in short - OpenDCRE tests are run through the Makefile. To run all tests, from the test
directory:

```
make test-x64
```

All tests are containerized for consistency and ease of deployment and integration. There are many test cases, so 
running the full suite of tests may take some time.

## License
OpenDCRE is released under GPLv2 - see LICENSE for more information.
