
<p align="center">
  <img alt="Synse Avatar" src="assets/avatar.png" width="200" />
  <h3 align="center">Synse Server</h3>
  <p align="center">An API to monitor and control physical and virtual infrastructure.</p>
</p>

---

[![Build Status](https://build.vio.sh/buildStatus/icon?job=vapor-ware/synse-server/master)](https://build.vio.sh/blue/organizations/jenkins/vapor-ware%2Fsynse-server/activity)
[![Code Coverage](https://codecov.io/gh/vapor-ware/synse-server/branch/master/graph/badge.svg)](https://codecov.io/gh/vapor-ware/synse-server)
[![Documentation Status](https://readthedocs.org/projects/synse/badge/?version=latest)](https://synse.readthedocs.io/en/latest/?badge=latest)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fvapor-ware%2Fsynse-server.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fvapor-ware%2Fsynse-server?ref=badge_shield)
![License](https://img.shields.io/github/license/vapor-ware/synse-server.svg)
![GitHub Release](https://img.shields.io/github/release/vapor-ware/synse-server.svg)

Synse Server is part of the [Synse Platform][synse]. It provides a simple HTTP API to make
gathering device metrics and issuing device commands easy. Synse is designed for lights-out
operation at edge data center sites, but can run in more traditional data center environments,
IoT labs, or as a monitoring and control solution for DIY projects.

With Synse's HTTP API and plugin backend, devices communicating over different protocols
(I²C, RS-485, or IPMI for example) can all be accessed via the same uniform API. Supporting
a new protocol or device is as simple as writing a new plugin with the [Synse SDK][sdk].

For more information about Synse Server and other components of the Synse platform,
see the [project documentation][documentation].

## Getting Started

Synse components are designed to run as containerized applications, making them easier
to compose, deploy, and manage (e.g. via [Docker Compose][docker-compose] or [Kubernetes][kubernetes]).
Getting the Synse Server image is as easy as:

```
docker pull vaporio/synse-server
```

A simple deployment of Synse Server with an emulator plugin backend (which provides simulated device data)
can be run with Docker Compose using the [`compose file`](docker-compose.yml) found in this repository:

```
docker-compose up -d
```

From there, you can test that Synse Server is running and reachable

```
curl http://localhost:5000/test
```

And see all of the devices it exposes via the emulator plugin

```
curl http://localhost:5000/v3/scan
```

See the [API Reference][api-ref] for more information on the API endpoints and
Synse's capabilities.

## Architecture Overview

<p align="center"><img src="assets/arch.svg" width="500" /></p>

Synse Server is a containerized service which provides an HTTP interface for interacting with
and controlling devices. Synse Server does not directly interface with any devices -- that job is
left to the plugins which are registered with a Synse Server instance. Plugins expose devices, collect
readings, and provide write access to those devices which support it. How they do this is dependent
on the devices themselves and will differ between those devices and protocols.

Synse Server acts as the "front-end" interface/router for all the different protocols/devices.
It exposes a uniform API to the user, routes commands to the proper device (e.g. to the plugin
that manages the referenced device), and does some aggregation, caching, and formatting of
the response data.

The general flow through Synse Server for a device read, for example, is:

- get an incoming HTTP request
- validate the specified device exists
- lookup the device's managing plugin
- dispatch a gRPC request to the plugin for that device
- await a response from the plugin
- take the data returned from the plugin and format it into the JSON response scheme
- return the data to the caller

## Feedback

Feedback for Synse Server or any component of the Synse platform is greatly appreciated!
If you experience any issues, find the documentation unclear, have requests for features,
or just have questions about it, we'd love to know. Feel free to open an issue for any
feedback you may have.

## Contributing

We welcome contributions to the project. The project maintainers actively manage the issues
and pull requests. If you choose to contribute, we ask that you either comment on an existing
issue or open a new one. This project follows the typical [GitHub Workflow][gh-workflow].

## License

Synse Server is released under the [GPL-3.0](LICENSE) license.

[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fvapor-ware%2Fsynse-server.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fvapor-ware%2Fsynse-server?ref=badge_large)

[synse]: https://github.com/vapor-ware/synse
[sdk]: https://github.com/vapor-ware/synse-sdk
[documentation]: https://synse.readthedocs.io/en/latest/
[docker-compose]: https://docs.docker.com/compose/
[kubernetes]: https://kubernetes.io/
[api-ref]: https://synse.readthedocs.io/en/latest/server/api.v3/
[gh-workflow]: https://guides.github.com/introduction/flow/
