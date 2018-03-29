
Synse Server
============

Synse Server provides a simple JSON API to monitor and control physical and virtual devices.
It provides a uniform HTTP interface for back-end plugins implementing various protocols,
such as RS-485, I²C, and IPMI. The Synse Server API makes it easy to read from and write
to devices, gather device meta-information, and scan for devices across multiple back-ends
through a curl-able interface.

Synse Server is created and maintained by Vapor IO under the GPL v2.0 license, and can be
found on `GitHub <https://github.com/vapor-ware/synse-server>`_.


Features
--------

- Simple ``curl``-able JSON API
- Asynchronous request processing
- Plugin architecture allows Synse Server to interface with any kind of device
- Internal gRPC API allows for plugins written in any language
- Read from devices
- Write to devices
- Enumerate all devices managed by plugins
- Get meta information on all devices
- Securable via TLS/SSL
- Dockerized for scalability and deployability


Architecture
------------

Synse Server is a micro-service that provides an HTTP interface for interaction and control
of devices. Synse Server does not directly interface with the devices -- that job is left to
the plugins that Synse Server can interface with. Plugins implement a given protocol to talk
to a given collection of devices, whether that is a serial protocol for sensors, or an HTTP
protocol for some external REST API is up to the plugin implementation.

.. image:: _static/arch.png

Synse Server really acts as the front-end interface for all the different protocols/devices.
It gives a uniform API to the user, routes commands to the proper device (e.g. to the plugin
that manages the referenced device), and does some aggregation, caching, and formatting of
the response data.

The general flow through Synse Server for a device read, for example, is:
- get an incoming HTTP request
- validate the specified device exists
- lookup the device's managing plugin
- dispatch a gRPC read request to the plugin for that device
- await a response from the plugin
- take the data returned from the plugin and format it into the JSON response scheme
- return the data to the caller

User Guide
----------

This part of the documentation describes how to get Synse Server, set it up, and how
to start using it.

.. toctree::
   :maxdepth: 2

   user/getting
   user/quickstart


Development
-----------

This part of the documentation describes how to develop with Synse Server and how to
contribute to the project.

.. toctree::
   :maxdepth: 2
