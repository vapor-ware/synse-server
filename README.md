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


## License
Synse is released under GPLv2 - see [LICENSE](license) for more information.


[cli]: https://github.com/vapor-ware/synse-cli
[docs]: http://opendcre.com
[license]: https://github.com/vapor-ware/synse-server/blob/master/LICENSE
[pkg-cloud]: https://packagecloud.io/VaporIO/synse/install
[prometheus]: https://github.com/vapor-ware/synse-prometheus