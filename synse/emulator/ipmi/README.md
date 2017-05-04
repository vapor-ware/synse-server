# Mock BMC for IPMI Emulation

This directory contains a Mock BMC modeled as a UDP server within a Docker container that is state-aware. It can be
used for limited testing of IPMI commands.

**Currently, it has only been tested with ipmitool** but further support (against pyghmi) will come.

## Using the Emulator

To use the emulator, you must have ipmitool installed. 

Spin up the emulator using the recipe
```
make ipmi-yml
```

which should bring up the emulator, binding docker-compose to it, so the output is visible. To run in the background, 
run with the `-d` flag.

Once done, you should be able to point ipmitool to it and issue commands (see below for currently supported commands), e.g.

```
ipmitool -H 127.0.0.1 -U ADMIN -P ADMIN chassis status
```

## Supported Commands
This list will grow as support is added.

* ipmitool chassis status
* ipmitool chassis power [status, on, off, cycle, reset]
* ipmitool chassis identify