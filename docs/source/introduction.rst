============
Introduction
============

Synse Server provides a JSON API for monitoring and control of data center and
IT equipment, including reading sensors and server power control - via.
numerous backend protocols such as IPMI, Redfish, SNMP, I2C, RS485, and PLC.
The API is easy to integrate into third-party monitoring, management and
orchestration providers. It provides a simple, ``curl``-able interface for
common and custom devops tasks.

.. note::
    Redfish support in Synse Server (v1.4.0) is largely still under development
    and testing, so it should be treated as a beta feature.


Features
--------

- Simple ``curl``-able JSON API.
- Analog and digital sensor support (temperature, thermistor, humidity,
  fan speed, pressure).
- Power control and status, including power consumption and power supply status.
- Asset information for servers.
- Physical and chassis location awareness.
- Chassis "identify" LED control and status.
- System boot target selection (hdd, pxe).
- Securable via TLS/SSL.
- Power line communications (PLC) - Synse Server commands can use PLC over a DC
  bus bar as transport layer.
- IPMI Bridge - Synse Server commands can use IPMI 2.0 over LAN as transport layer.
- Redfish support (beta) - Synse Server commands can use Redfish over LAN as
  transport layer.

Architecture
------------

Synse Server is a Dockerized service designed to run in a microservice
architecture. It exposes a JSON API via an HTTP endpoint in the Synse Server
container. The HTTP endpoint is comprised of Nginx as the front-end with uwsgi
as a reverse proxy for a Python Flask application. Within the Flask application
exists modular "device bus" definitions to define their own protocol-specific
backends. The Synse Server endpoints route and dispatch incoming commands to
the appropriate device bus for handling.

The Synse Server device bus is comprised of a set of boards and devices,
individually addressable, and globally scannable for a real-time inventory of
addressable devices. The device bus allows devices to be read and written, and
for various actions to be carried out, such as power control (on/off/cycle/status).
Additionally, when a physical device bus is not present, a software emulator
can be used to simulate API commands and functionality.

All included components of Synse Server can be customized, integrated and
secured via configuration file (nginx, uwsgi).

Applications
------------

Synse Server can be used as an open platform for monitoring and managing data
center hardware, software and environmental characteristics. Since Synse Server
is containerized, there are a wide variety of options for deployments,
integrations, network connectivity, etc. Community support helps Synse Server
grow, and enables new functionality.
