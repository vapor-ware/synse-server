=============
API Reference
=============

The examples below assume OpenDCRE is running on a given <ipaddress> and <port>.  The default port for OpenDCRE is TCP port 5000.  Currently, all commands are GET requests; a future version will expose these commands via POST as well.

Scan
====

Description
-----------

- The ``scan`` command polls boards and devices attached to the board.  The ``scan`` command takes a ``board_id`` as its argument, and returns an array of board and device descriptors. If no ``board_id`` is provided, the ``scan`` command scans all boards on the device bus.

Notes
-----

- It is likely a good idea for applications to scan for all boards on startup, to ensure a proper map of boards and devices is available to the application.  Mismatches of board and device types and identifiers will result in 500 errors being returned for various commands that rely on these values mapping to actual hardware.

Request Format
--------------

- Scan devices on a specific ``board_id``:

::

    http://<ipaddress>:<port>/opendcre/<version>/scan/<board_id>

- Scan all boards on the device bus:

::

    http://<ipaddress>:<port>/opendcre/<version>/scan

Parameters
----------

- ``board_id`` (optional) : Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper 3 bytes of ``board_id`` are reserved for future use in OpenDCRE v1.1.  IPMI Bridge board has a special ``board_id`` of 40000000.

Request Example
---------------
::

    http://opendcre:5000/opendcre/1.1/scan

Response Schema
---------------

::

    {
        "$schema": "http://schemas.vapor.io/opendcre/v1.1/opendcre-1.1-boards-devices",
        "title": "OpenDCRE Boards and Devices",
        "type": "object",
        "properties": {
            "boards": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "board_index": {
                            "type": "string"
                        },
                        "devices": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "device_id": {
                                        "type": "string"
                                    },
                                    "device_type": {
                                        "type": "string",
                                        "enum": [
                                            "temperature",
                                            "thermistor",
                                            "humidity",
                                            "led",
                                            "ipmb",
                                            "power",
                                            "door_lock",
                                            "current",
                                            "pressure",
                                            "mone"
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }


Example Response
----------------

::

    {
      "boards": [
        {
          "board_id": "00000001",
          "devices": [
            {
              "device_id": "01ff",
              "device_type": "thermistor"
            },
            {
              "device_id": "02ff",
              "device_type": "none"
            }
          ]
        },
        {
          "board_id": "00000002",
          "devices": [
            {
              "device_id": "01ff",
              "sensor_type": "thermistor"
            },
            {
              "device_id": "02ff",
              "device_type": "none"
            }
          ]
        }
      ]
    }

Errors
------

- Returns error (500) if scan command fails, or if ``board_id`` corresponds to an invalid ``board_id``.

Version
=======

Description
-----------

Return version information about a given board given its ``board_id``.

Request Format
--------------
::

    http://<ipaddress>:<port>/opendcre/<version>/version/<board_id>

Parameters
----------

``board_id`` : Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper 3 bytes of ``board_id`` are reserved for future use in OpenDCRE v1.1.  IPMI Bridge board has a special ``board_id`` of 40000000.

Request Example
---------------
::

    https://opendcre:5000/opendcre/1.0/version/00000001

Response Schema
---------------

::

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.1/opendcre-1.1-version",
      "title": "OpenDCRE Board Version",
      "type": "object",
      "properties": {
        "api_version": {
          "type": "string"
        },
        "firmware_version": {
          "type": "string"
        },
        "opendcre_version": {
          "type": "string"
        }
      }
    }

Example Response
----------------

::

    {
      "api_version": "1.1", 
      "firmware_version": "OpenDCRE Emulator v1.1.0", 
      "opendcre_version": "1.1.0"
    }

Errors
------

Returns error (500) if version retrieval does not work or if ``board_id`` specifies a nonexistent board.

Read Device
===========

Description
-----------

- Read a value from the given ``board_id`` and ``device_id`` for a specific ``device_type``.  The specified ``device_type`` must match the actual physical device type (as reported by the ``scan`` command), and is used to return a translated raw reading value (e.g. temperature in C for a thermistor) based on the existing algorithm for a given sensor type.  The raw value is also returned.

Request Format
::

    http://<ipaddress>:<port>/opendcre/<version>/read/<device_type>/<board_id>/<device_id>

Parameters
----------

- ``device_type``:  String value (lower-case) indicating what type of device to read:
    - thermistor
    - temperature  (not implemented yet)
    - current (not implemented yet)
    - humidity (not implemented yet)
    - led (not implemented yet)
    - ipmb (not implemented yet)
    - door_lock (not implemented yet)
    - pressure (not implemented yet)
    - none (**Note**:  reading a "none" device will result in a 500 error)

- ``board_id`` : Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper 3 bytes of ``board_id`` are reserved for future use in OpenDCRE v1.1.  IPMI Bridge board has a special ``board_id`` of 40000000.

- ``device_id`` : The device to read on the specified board.  Hexadecimal string representation of a 2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to  OpenDCRE matches the ``device_type`` specified in the command for the given device - else, a 500 error is returned.

Request Example
---------------
::

    http://opendcre:5000/opendcre/1.1/read/thermistor/00000001/01FF

Response Schema
---------------

::

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.1/opendcre-1.1-thermistor-reading",
      "title": "OpenDCRE Thermistor Reading",
      "type": "object",
      "properties": {
        "sensor_raw": {
          "type": "number"
        },
        "temperature_c": {
          "type": "number"
        }
      }
    }

Example Response
----------------

::

    {
      "sensor_raw": 755,
      "temperature_c": 19.73
    }

Errors
------

- If a sensor is not readable or does not exist, an error (500) is returned.

Read Asset Info
===============

Description
-----------

- Read asset information from the given ``board_id`` and ``device_id`` for a specific ``device_type``.  The specified ``device_type`` must match the actual physical device type (as reported by the ``scan`` command), and is used to return asset information (e.g. IP address, MAC address, Asset Tag, etc.) about a given device.  Only devices of ``device_type`` of ``power`` support retrieval of asset information; IPMI ``power`` devices support read of asset information, but do not support write of asset information.

Request Format
--------------
::
    
    http://<ipaddress>:<port>/opendcre/<version>/read/<device_type>/<board_id>/<device_id>/info

Parameters
----------

- ``device_type``:  String value (lower-case) indicating what type of device to read:
    - power (**Note**:  all other device types unsupported in this version of OpenDCRE).

- ``board_id`` : Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper 3 bytes of ``board_id`` are reserved for future use in OpenDCRE v1.1.  IPMI Bridge board has a special ``board_id`` of 40000000.  IPMI BMC asset information is readable, but not writeable.

- ``device_id`` : The device to read asset information for on the specified board.  Hexadecimal string representation of a 2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to OpenDCRE matches the ``device_type`` specified in the command for the given device - else, a 500 error is returned.

Request Example
---------------
::

    http://opendcre:5000/opendcre/1.1/read/power/00000001/01FF/info

Response Schema
---------------

::

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.1/opendcre-1.1-asset-info-reading",
      "title": "OpenDCRE Asset Info Reading",
      "type": "object",
      "properties": {
        "board_id": {
          "type": "string"
        },
        "device_id: {
          "type": "string"
        },
        "asset_info: {
          "type": "string"
        }
      }
    }

Alternately, for IPMI devices:

::

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.1/opendcre-1.1-asset-info-reading",
      "title": "OpenDCRE Asset Info Reading",
      "type": "object",
      "properties": {
        "board_id": {
          "type": "string"
        },
        "device_id: {
          "type": "string"
        },
        "asset_info: {
          "type": "string"
        },
        "bmc_ip: {
          "type": "string"
        }
      }
    }

Example Response
----------------

::

    {
      "board_id": "00000001",
      "device_id": "01FF",
      "asset_info": "example asset information"
    }

Alternately, for IPMI devices:

::

    {
      "board_id": "00000001",
      "device_id": "01FF",
      "asset_info": "example IPMI asset information",
      "bmc_ip": "123.124.10.100"
    }

Errors
------

- asset info is not readable or does not exist, an error (500) is returned.

Write Asset Info
================

Description
-----------

- Write asset information from the given ``board_id`` and ``device_id`` for a specific ``device_type``.  The specified ``device_type`` must match the actual physical device type (as reported by the ``scan`` command), and is used to set asset information (e.g. IP address, MAC address, Asset Tag, etc.) for a given device.  Only devices of ``device_type`` of ``power`` support set and retrieval of asset information; IPMI ``power`` devices support read of asset information, but do not support write of asset information.  Attempting to write asset information for an IPMI device will result in a 500 error.

Request Format
--------------
::

    http://<ipaddress>:<port>/opendcre/<version>/write/<device_type>/<board_id>/<device_id>/info/<value>

Parameters
----------

- ``device_type``:  String value (lower-case) indicating what type of device to write asset info for:
    - power (**Note**:  all other device types unsupported in this version of OpenDCRE).

- ``board_id`` : Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper 3 bytes of ``board_id`` are reserved for future use in OpenDCRE v1.1.  IPMI Bridge board has a special ``board_id`` of 40000000.  IPMI BMC asset information is readable, but not writeable.

- ``device_id`` : The device to read asset information for on the specified board.  Hexadecimal string representation of a 2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to OpenDCRE matches the ``device_type`` specified in the command for the given device - else, a 500 error is returned.

- ``value`` : The string value to set for asset information for the given device.  Max length of this string value is 127 bytes.  Overwrites any value previously stored in the ``asset_info`` field.

Request Example
---------------
::

    http://opendcre:5000/opendcre/1.1/write/power/00000001/01FF/info/192.100.10.1

Response Schema
---------------

::

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.1/opendcre-1.1-asset-info-response",
      "title": "OpenDCRE Asset Info Response",
      "type": "object",
      "properties": {
        "board_id": {
          "type": "string"
        },
        "device_id: {
          "type": "string"
        },
        "asset_info: {
          "type": "string"
        }
      }
    }

Example Response
----------------

::

    {
      "board_id": "00000001",
      "device_id": "01FF",
      "asset_info": "example asset information"
    }

Errors
------

- If asset info is not writeable or does not exist, an error (500) is returned.

Write Device
============

Description
-----------

- Write to device bus to a writeable device.  The write command is followed by the ``device_type``, ``board_id`` and ``device_id``, with the final field of the request being the data sent to the device.

Status
------

- Not yet implemented.

Power
=====

Description
-----------

- Control device power, and/or retrieve its power supply status.

Request Format
--------------
::

    http://<ipaddress>:<port>/opendcre/<version>/power/<command>/<board_id>/<device_id>

Parameters
----------

- ``board_id`` : Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper 3 bytes of ``board_id`` are reserved for future use in OpenDCRE v1.1.  IPMI Bridge board has a special ``board_id`` of 40000000.

- ``device_id`` : The device to issue power command to on the specified board.  Hexadecimal string representation of 2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to the OpenDCRE HAT is ``power`` - else, a 500 error is returned.

- ``command`` : 
    - ``on`` : Turn power on to specified device.
    - ``off`` : Turn power off to specified device.
    - ``cycle`` : Power-cycle the specified device.
    - ``status`` : Get power status for the specified device.

For all commands, power status is returned as the command's response.

Request Example
---------------
::

    http://opendcre:5000/opendcre/1.1/power/on/00000001/01ff

Response Schema
---------------

::

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.1/opendcre-1.1-power-status",
      "title": "OpenDCRE Power Status",
      "type": "object",
      "properties": {
        "input_power": {
          "type": "number"
        },
        "input_voltage": {
          "type": "number"
        },
        "output_current": {
          "type": "number"
        },
        "over_current": {
          "type": "boolean"
        },
        "pmbus_raw": {
          "type": "string"
        },
        "power_ok": {
          "type": "boolean"
        },
        "power_status": {
          "type": "string"
        },
        "under_voltage": {
          "type": "boolean"
        }
      }
    }

Example Response
----------------

::

    {
      "input_power": 0.0, 
      "input_voltage": 0.0, 
      "output_current": -25.70631970260223, 
      "over_current": false, 
      "pmbus_raw": "0,0,0,0", 
      "power_ok": true, 
      "power_status": "on", 
      "under_voltage": false
    }

Errors
------

- If a power action fails, or an invalid board/device combination are specified, an error (500) is returned.

Test
====

Description
-----------

- The test command may be used to verify that the OpenDCRE endpoint is up and running, but without attempting to address the device bus.  The command takes no arguments, and if successful, returns a simple status message of "ok".

Request Format
--------------
::

   http://<ipaddress>:<port>/opendcre/<version>/test

Response Schema
---------------

::

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.1/opendcre-1.1-test-status",
      "title": "OpenDCRE Test Status",
      "type": "object",
      "properties": {
        "status": {
          "type": "string"
        }
      }
    }

Example Response

::

    {
      "status": "ok" 
    }

Errors
------

- If the endpoint is not running no response will be returned, as the command will always return the response above while the endpoint is functional.
