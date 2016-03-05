===========
IPMI Bridge
===========

About
-----

The Vapor IPMI bridge allows users of OpenDCRE to use both bus-bar-based power line communications, and LAN-based IPMI communications for equipment monitoring and management. The IPMI bridge is included with OpenDCRE v1.1.0 and later, and supports power control and status via IPMI using the OpenDCRE REST API.

Requirements
------------

- OpenMistOS must be connected to a wired LAN network that can reach all BMCs configured to be managed over OpenDCRE.
- Knowledge of BMC IP addresses, authentication types and usernames and passwords (where applicable) required.
- Authentication Types supported:
    - NONE (no username or password, not recommended)
    - PASSWORD (username and password, sent in clear text, not recommended)
    - MD2
    - MD5

Configuration
-------------

The Vapor IPMI bridge is configured via the ``bmc_config.json`` file, located in the top level of the OpenDCRE distribution.  An example file, ``bmc_config_sample.json`` is included with OpenDCRE, and may be modified to one's environment.

All IPMI BMCs successfully configured will show up on a ``scan`` command result as devices under ``board_id`` 40000000.
::

  {
    "bmcs": [
      {
        "bmc_device_id": 1,
        "bmc_ip": "192.168.1.118",
        "username": "username",
        "password": "password",
        "auth_type": "MD5",
        "asset_info": "example BMC info"
      }
    ]
  }

For each BMC supported, an entry is added to the ``bmcs`` list above.  Each entry must include:

- ``bmc_device_id`` - a numeric value corresponding to the ``device_id``, must be unique.
- ``bmc_ip`` - the IP address (as a string) corresponding to the BMC to be managed.  IP address must be reachable by OpenMistOS.
- ``username`` - the username to use in connecting to the BMC - may be an empty string if no username is used.
- ``password`` - the password to use in connecting to the BMC - may be an empty string if no username is used.
- ``auth_type`` - the type of authentication to use in connecting to the BMC, supported values:
    - ``NONE``
    - ``PASSWORD``
    - ``MD2``
    - ``MD5``
- ``asset_info`` - a string (up to 127 bytes) containing asset information about the given BMC/server, returned via the read-info command for the device.

Once the configuration file has been successfully edited, rebuild the OpenDCRE Docker container, and verify the configured BMC devices are returned via a ``scan`` command under board 40000000.

BMC devices will show up as ``power`` devices, and all ``power`` commands (``on``, ``off``, ``cycle``, ``status``) are supported.  

Reading asset information about a given BMC can be carried out via the ``read`` command for the info field for the given BMC device.  BMC ``asset_info`` is readable via the OpenDCRE endpoint, but is not writeable via the endpoint.

If the configuration file contains errors or is missing, no devices will show up under the IPMI ``board_id`` on a ``scan`` command.
