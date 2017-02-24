====================
DeviceBus Interfaces
====================

At the heart of OpenDCRE is the notion of "device bus" (or "devicebus"), which is so-named due to the original
single-purpose PLC bus, and can now be said to describe "devices and busses" supported by OpenDCRE. Currently, there
are three devicebus interfaces supported by OpenDCRE: PLC, IPMI, and Redfish (beta).

.. _opendcre-plc-device:

PLC Device
----------
.. versionadded:: 1.0.0

PLC (Power Line Communications) support was the first (and only) mode available in early (pre v1.0) versions of
OpenDCRE. The PLC Device provides support for serial-based communication between OpenDCRE and the Vapor Chamber.

Supported Commands
^^^^^^^^^^^^^^^^^^
The :ref:`opendcre-test-command` and :ref:`opendcre-service-version-command` are supported by all devicebus types. Below
are the commands which are supported for PLC Devices. See the :ref:`opendcre-api-ref` for details on all commands.

=========== =========
Command     Supported
=========== =========
Version     True
Scan        True
Scan All    True
Read        True
Power       True
Asset       True
Boot Target True
Chamber LED True
LED         True
Fan         True
Host Info   True
=========== =========

Configuration
^^^^^^^^^^^^^

PLC Device configurations are specified under the ``devices`` field of the OpenDCRE :ref:`opendcre-configuration-options`.
A simple example configuration is given below, followed by descriptions of the fields presented in the example.

.. code-block:: json

    {
      "devices": {
        "plc": {
          "from_config": "plc_config.json"
        }
      }
    }

:from_config:
    The file which specifies the rack and device configurations for devices managed through OpenDCRE. See below for an
    example of these configurations.

:config:
    An alternative to ``from_config`` - this field allows one to specify the rack and device configurations in this
    configuration file as opposed to a separate one. Generally, it is recommended to use ``from_config`` over this, as
    it keeps things cleaner, but if only a few devices are being specified, it may be easier to define their
    configurations under this field.

As mentioned above, the ``from_config`` and ``config`` fields specify the device-specific configurations. The JSON example
below could either be specified under the ``config`` field, or in the file specified by the ``from_config`` field.

.. code-block:: json

    {
      "racks": [
        {
          "rack_id": "rack_1",
          "lockfile": "/tmp/OpenDCRE.lock",
          "hardware_type": "emulator",
          "devices": [
            {
              "device_name": "/dev/ttyAMA0",
              "retry_limit": 3,
              "timeout": 0.25,
              "time_slice": 75,
              "bps": 115200
            }
          ]
        }
      ]
    }

:racks:
    OpenDCRE is capable of managing multiple racks' worth of BMCs, so the top-level configuration parameter "racks"
    consists of a list of rack definitions (in the above example, only a single rack with rack_id of "rack_1" is
    specified).

:rack_id:
    For each rack configured with OpenDCRE, a "rack_id" must be specified to identify that rack. In the example
    above, "rack_1" is the rack_id. This is the same rack_id specified in OpenDCRE REST API commands. When multiple
    devicebus types are defined for an OpenDCRE configuration, devices in common rack_ids are merged together into the
    rack record in scan results for that rack. In other words, devices from multiple devicebus types may be assigned to
    the same rack in OpenDCRE, assuming the same rack_id is used in each of their configurations.

:lockfile:
    At the rack-level, a lockfile path and filename may be defined such that all devices belonging to that rack share
    a common lockfile, ensuring serial and exclusive access to the bus. *(This lockfile may also be shared with other
    racks and bus types when shared bus/hardware access must be serial across racks and bus types.)*

:hardware_type:
    Indicates whether hardware is emulated ("emulator") or "real". In the case of "emulator", device interface
    implementations may use an alternate code path (e.g. for testing or demonstration purposes) routed to an emulator,
    as opposed to taking physical hardware actions. When using OpenDCRE with emulator backing, "emulator" should be
    specified here, otherwise, when OpenDCRE is used with real hardware, "real" should be specified for hardware_type.

:devices:
    Within a given rack, one or more PLC devices may be specified for brokering bus access to the PLC bus. In most
    cases involving PLC, only a single device is present, corresponding to the PLC modem serial device and its
    configuration, however multiple devices can be supported (e.g. in the case of multiple PLC buses or modems
    in a single rack).

:device_name:
    The path and file name to the serial TTY device for PLC communications. When ``hardware_type`` is "emulator",
    this typically corresponds to the OpenDCRE-side of a socat-paired virtual serial connection (e.g.
    /dev/ttyVapor001). When ``hardware_type`` is "real", this corresponds to the physical serial device mapped into
    the OpenDCRE container for use with PLC for reading and writing.

:retry_limit:
    Configures the number of retries permitted (in case of line noise or bus errors) before an error is returned.
    The default should be sufficient in most cases. **(default: 3)**

:timeout:
    A decimal value indicating the time, in seconds, to wait for a response to an OpenDCRE PLC bus command before
    timing out. The default value is typically sufficient in physical hardware cases as well as with the OpenDCRE
    PLC emulator. **(default: 0.25)**

:time_slice:
    The time slice used during a scan command to enumerate all PLC devices on the PLC bus. This value is used to allow
    devices to use their internal board_id and the time slice value to determine which window to use in responding to
    the scan command. Users generally should not alter this value. **(default: 75)**

:bps:
    The bits per second configuration value to use for PLC communications on the PLC bus. This generally should not
    be modified by users. **(default: 115200)**

If a field is missing, or the PLC configuration file is improperly formatted, OpenDCRE PLC capabilities will not be available.

.. _opendcre-ipmi-device:

IPMI Device
-----------
.. versionadded:: 1.1.0

IPMI Devices allow users of OpenDCRE to issue LAN-based IPMI commands using the OpenDCRE REST API.

Supported Commands
^^^^^^^^^^^^^^^^^^
The :ref:`opendcre-test-command` and :ref:`opendcre-service-version-command` are supported by all devicebus types. Below
are the commands which are supported for IPMI Devices. See the :ref:`opendcre-api-ref` for details on all commands.

=========== =========
Command     Supported
=========== =========
Version     True
Scan        True
Scan All    True
Read        True
Power       True
Asset       True
Boot Target True
Chamber LED False
LED         True
Fan         True
Host Info   True
=========== =========

Requirements
^^^^^^^^^^^^

- OpenDCRE must be connected to a wired LAN network that can reach all BMCs configured to be managed over OpenDCRE.
- Knowledge of BMC IP addresses, ports, usernames, and passwords (where applicable) required.

.. versionchanged:: 1.3.0
    Previously, a custom IPMI interface was used which required the specification of authentication type, integrity
    type, and encryption type. Now, `pyghmi <https://github.com/openstack/pyghmi>`_ is used as the IPMI interface,
    which does not expose customization for those parameters, thus they need no longer be specified in the configuration
    file.


Configuration
^^^^^^^^^^^^^

IPMI Device configurations are specified under the ``devices`` field of the OpenDCRE :ref:`opendcre-configuration-options`.
A simple example configuration is given below, followed by descriptions of the fields presented in the example.

.. code-block:: json

    {
      "devices": {
        "ipmi": {
          "scan_on_init": true,
          "device_initializer_threads": 4,
          "from_config": "bmc_config.json"
        }
      }
    }

:from_config:
    The file which specifies the rack and BMC configurations for BMCs managed through OpenDCRE. See below for an example
    of these configurations.

:config:
    An alternative to ``from_config`` - this field allows one to specify the rack and BMC configurations in this configuration
    file as opposed to a separate one. Generally, it is recommended to use ``from_config`` over this, as it keeps things
    cleaner, but if only a few BMCs are being specified, it may be easier to define their configurations under this field.

:scan_on_init:
    *(optional)* A flag which determines whether or not the IPMI Devices will perform a scan operation on device
    initialization, or if it will be deferred for later. Typically, it is a good idea to scan on initialization, as
    that is how the board record is created and how the devices off of the BMC are found. Deferring scan to a time
    post-initialization can be useful in testing or if there is high network latency and one does not want the slow
    initialization process to delay OpenDCRE startup. **(default: true)**

:device_initializer_threads:
    *(optional)* The number of threads to use when initializing IPMI Devices. Since IPMI devices use LAN communication,
    initializing multiple devices can be done in parallel. **(default: 1)**

As mentioned above, the ``from_config`` and ``config`` fields specify the BMC-specific configurations. The JSON example
below could either be specified under the ``config`` field, or in the file specified by the ``from_config`` field.

.. code-block:: json

    {
      "racks": [
        {
          "rack_id": "rack_1",
          "bmcs": [
            {
              "bmc_ip": "192.168.1.110",
              "username": "ADMIN",
              "password": "ADMIN"
            },
            {
              "bmc_ip": "192.168.1.111",
              "bmc_port": 623,
              "username": "ADMIN",
              "password": "ADMIN",
              "hostnames": ["atom"],
              "ip_addresses": ["192.169.1.111"]
            }
          ]
        }
      ]
    }

:racks:
    OpenDCRE is capable of managing multiple racks' worth of BMCs, so the top-level configuration parameter "racks"
    consists of a list of rack definitions (in the above example, only a single rack with rack_id of "rack_1" is
    specified).

:rack_id:
    For each rack configured with OpenDCRE, a "rack_id" must be specified to identify that rack. In the example
    above, "rack_1" is the rack_id. This is the same rack_id specified in OpenDCRE REST API commands. When multiple
    devicebus types are defined for an OpenDCRE configuration, devices in common rack_ids are merged together into the
    rack record in scan results for that rack. In other words, devices from multiple devicebus types may be assigned to
    the same rack in OpenDCRE, assuming the same rack_id is used in each of their configurations.

:bmcs:
    The "bmcs" field consists of a list of zero or more BMC configuration records. Each BMC configuration record
    corresponds to an individual BMC situated in the configured rack.

:bmc_ip:
    The IP address (or hostname) of the BMC being configured. It must be a string value and the BMC IP must also be
    accessible over LAN by the OpenDCRE service.

:username:
    The username used to connect to the BMC. For OpenDCRE to be able to fully control a remote server, the username
    should have sufficient permissions on the remote BMC.

:password:
    The password used to connect to the BMC for the given username.

:bmc_port:
    *(optional)* The UDP port number of the BMC. Must be specified as an integer. **(default: 623)**

:hostnames:
    *(optional)* A list of known hostnames for the remote system that may be used in place of the board_id of the BMC
    for OpenDCRE REST API requests. This list may be augmented by OpenDCRE in case of DCMI support, where DCMI may be
    used to get host identification as well. At minimum, the contents of the "hostnames" list are returned in scan and
    host_info responses related to the given system.

:ip_addresses:
    *(optional)* A list of known IP addresses for the remote system that may be used in place of the board_id of the
    BMC for OpenDCRE REST API requests. This list may be augmented by OpenDCRE to include the bmc_ip (if not already
    included in this list), allowing access to any IPMI device via OpenDCRE REST API by using the BMC IP or known
    IP addresses in place of board_id. Contents of the "ip_addresses" list are returned in scan and host_info responses
    related to the given system.


If a field is missing, or the IPMI configuration file is improperly formatted, OpenDCRE IPMI capabilities will not be available.


Supported Devices
^^^^^^^^^^^^^^^^^
Currently, the supported devices for IPMI include:

- power
- system
- LED
- fan
- power supply
- temperature
- voltage


Tested BMCs
^^^^^^^^^^^
OpenDCRE v1.3 has been tested and verified to be compatible with IPMI 2.0 connections and commands for the following BMCs:

    - ASpeed AST2400 (via HPE CL7100)
    - Nuvoton WPCM450RA0BK (via SuperMicro X7SPA-HF)
    - ASpeed AST2050 (via Tyan S8812)
    - ASpeed AST1250 (via Freedom)

The OpenDCRE community welcomes testing and bug reports against other BMCs and system types.


.. _opendcre-redfish-device:

Redfish Device
--------------
.. versionadded:: 1.3.0

.. warning::
    Redfish support is in beta as of OpenDCRE v1.3.0

Redfish Devices map Redfish schema into OpenDCRE, allowing for LAN-based Redfish commands using the OpenDCRE REST API.


Supported Commands
^^^^^^^^^^^^^^^^^^
The :ref:`opendcre-test-command` and :ref:`opendcre-service-version-command` are supported by all devicebus types. Below
are the commands which are supported for Redfish Devices. See the :ref:`opendcre-api-ref` for details on all commands.

=========== =========
Command     Supported
=========== =========
Version     True
Scan        True
Scan All    True
Read        True
Power       True
Asset       True
Boot Target True
Chamber LED False
LED         True
Fan         True
Host Info   True
=========== =========

Configuration
^^^^^^^^^^^^^

Redfish Device configurations are specified under the ``devices`` field of the OpenDCRE :ref:`opendcre-configuration-options`.
A simple example configuration is given below, followed by descriptions of the fields presented in the example.

.. code-block:: json

    {
      "devices": {
        "redfish": {
          "scan_on_init": true,
          "device_initializer_threads": 4,
          "from_config": "redfish_config.json"
        }
      }
    }

:from_config:
    The file which specifies the rack and device configurations for devices managed through OpenDCRE. See below for an
    example of these configurations.

:config:
    An alternative to ``from_config`` - this field allows one to specify the rack and device configurations in this
    configuration file as opposed to a separate one. Generally, it is recommended to use ``from_config`` over this, as
    it keeps things cleaner, but if only a few devices are being specified, it may be easier to define their
    configurations under this field.

:scan_on_init:
    *(optional)* A flag which determines whether or not the Redfish Devices will perform a scan operation on device
    initialization, or if it will be deferred for later. Typically, it is a good idea to scan on initialization, as
    that is how the board record is created and how the devices are found. Deferring scan to a time
    post-initialization can be useful in testing or if there is high network latency and one does not want the slow
    initialization process to delay OpenDCRE startup. **(default: true)**

:device_initializer_threads:
    *(optional)* The number of threads to use when initializing Redfish Devices. Since Redfish devices use LAN
    communication, initializing multiple devices can be done in parallel. **(default: 1)**

As mentioned above, the ``from_config`` and ``config`` fields specify the device-specific configurations. The JSON example
below could either be specified under the ``config`` field, or in the file specified by the ``from_config`` field.

.. code-block:: json

    {
      "racks": [
        {
          "rack_id": "rack_1",
          "servers": [
            {
              "redfish_ip": "192.168.1.110",
              "redfish_port": "5040",
              "timeout": 5,
              "username": "ADMIN",
              "password": "ADMIN",
              "hostnames": ["redfish-server-1"],
              "ip_addresses": ["192.168.1.110"]
            }
          ]
        }
      ]
    }

:racks:
    OpenDCRE is capable of managing multiple racks' worth of servers, so the top-level configuration parameter "racks"
    consists of a list of rack definitions (in the above example, only a single rack with rack_id of "rack_1" is
    specified).

:rack_id:
    For each rack configured with OpenDCRE, a "rack_id" must be specified to identify that rack. In the example
    above, "rack_1" is the rack_id. This is the same rack_id specified in OpenDCRE REST API commands. When multiple
    devicebus types are defined for an OpenDCRE configuration, devices in common rack_ids are merged together into the
    rack record in scan results for that rack. In other words, devices from multiple devicebus types may be assigned to
    the same rack in OpenDCRE, assuming the same rack_id is used in each of their configurations.

:servers:
    The servers field consists of a list of zero or more Redfish server configuration records. Each Redfish configuration
    record corresponds to an individual Redfish server situated in the configured rack.

:redfish_ip:
    The IP address (or hostname) of the Redfish server being configured. The Redfish IP must also be accessible over
    LAN by the OpenDCRE service.

:redfish_port:
    The port which the Redfish server is listening on.

:timeout:
    The timeout, in seconds, for the HTTP request being made to the Redfish server before an error is raised.

:username:
    The username used to connect to the Redfish server.

:password:
    The password used to connect to the Redfish server for the given username.

:hostnames:
    A list of known hostnames for the remote system that may be used in place of the board_id for the Redfish server
    for OpenDCRE REST API requests.

:ip_addresses:
    A list of known IP addresses for the remote system that may be used in place of the board_id for the Redfish
    server for OpenDCRE REST API requests.


If a field is missing, or the Redfish configuration file is improperly formatted, OpenDCRE Redfish capabilities will not be available.