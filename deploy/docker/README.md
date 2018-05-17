# Deploying with Docker Compose
This directory contains examples for [docker-compose][docker-compose] based deployments
of Synse Server (v2.0+) with the containerized Emulator Plugin.

## Deployments
As a general note - the Emulator Plugin does not need to be containerized. In
fact, it is built into non-slim Synse Server 2.0+ images so that it can run
alongside Synse Server, providing an easy way to get started/demo/play with it.

In this case, we use a containerized version of the same emulator in order to
give us a plugin that is not dependent on any platform or hardware. This makes 
the examples here a good place to get started. Additionally, we use a slim version
of Synse Server as to prove that the data is coming from the external emulator only.

There are two docker-compose based deployments here. The only difference between
the two is how Synse Server and the Plugin are configured to communicate. Currently,
the [plugin SDK][synse-sdk] (via the [internal gRPC API][synse-grpc]) supports 
communication via:
- TCP
- UNIX socket

The two deployments here serve as an example on how to configure plugin and Synse
Server for both of those cases.

> **Note**: The difference is entirely in the configuration, not in the version of
> the plugin or Synse Server. See the compose files and the corresponding config
> files in the `config/` subdirectory to see how the two deployments differ.


## Setup

You will need the Synse Server image and the emulator plugin image. These can
either be built locally, or can be pulled from DockerHub.
```shell
# synse server
docker pull vaporio/synse-server

# emulator plugin
docker pull vaporio/emulator-plugin
```

If these images do not exist locally, `docker-compose` will pull them when the
example compose files are run.

## Usage
Running either of the examples is pretty straightforward; there are Makefile
targets for each deployment. To run the deployment that uses TCP-based communication
between Synse Server and the plugin:
```
make tcp
```

To run the deployment that uses UNIX socket-based communication between 
Synse Server and the plugin:
```
make unix
```

Once up and running, Synse Server should behave the same in both cases. That is to
say, the data that Synse Server surfaces should be the same (it comes from the same
emulator image). See the compose files and their related config files  (in the `config/`
subdirectory) to see the differences between deployments.

Once one of the deployments is running, you can test out that Synse Server is reachable.
```
curl localhost:5000/synse/test
```

If successful, you are ready to go. Next, perform a scan to see everything that is available
via the plugin:
```
curl localhost:5000/synse/2.0/scan
```

This should give back a set of devices - in particular:
- 1 fan device
- 2 LED devices
- 1 airflow device
- 1 humidity device
- 2 pressure devices
- 5 temperature devices

If you look at the log output of the Emulator Plugin , you should see that these results
match up with what that plugin had registered on startup.

[docker-compose]: https://docs.docker.com/compose/install/
[synse-sdk]: https://github.com/vapor-ware/synse-sdk
[synse-grpc]: https://github.com/vapor-ware/synse-server-grpc
