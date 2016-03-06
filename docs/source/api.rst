=============
API Reference
=============

The examples below assume OpenDCRE is running on a given <ipaddress> and <port>.  The default port for OpenDCRE is TCP port 5000.  Currently, all commands are GET requests; a future version will expose these commands via POST as well.

Scan
====

Description
-----------

The ``scan`` command polls boards and devices attached to the board.  The ``scan`` command takes a ``board_id`` as its argument, and returns an array of board and device descriptors. If no ``board_id`` is provided, the ``scan`` command scans all boards on the device bus.

.. note::
    It is likely a good idea for applications to scan for all boards on startup, to ensure a proper map of boards and devices is available to the application.  Mismatches of board and device types and identifiers will result in 500 errors being returned for various commands that rely on these values mapping to actual hardware.

Request Format
--------------

Scan devices on a specific ``board_id``:
::

    http://<ipaddress>:<port>/opendcre/<version>/scan/<board_id>

Scan all boards on the device bus:
::

    http://<ipaddress>:<port>/opendcre/<version>/scan

Parameters
----------

:board_id: (optional) Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of ``board_id`` reserved for future use in OpenDCRE.  IPMI Bridge boards have a special ``board_id`` of 40NNNNNN (where NNNNNN is the hex string id of each configured BMC).

Request Example
---------------
::

    http://opendcre:5000/opendcre/1.2/scan

Response Schema
---------------

.. code-block:: json

    {
        "$schema": "http://schemas.vapor.io/opendcre/v1.2/opendcre-1.2-boards-devices",
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
                                            "system",
                                            "power",
                                            "fan_speed",
                                            "pressure"
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

.. code-block:: json

    {
      "boards": [
        {
          "board_id": "00000001",
          "devices": [
            {
              "device_id": "0001",
              "device_type": "thermistor"
            },
            {
              "device_id": "0002",
              "device_type": "fan_speed"
            }
          ]
        },
        {
          "board_id": "00000002",
          "devices": [
            {
              "device_id": "0001",
              "sensor_type": "thermistor"
            },
            {
              "device_id": "2000",
              "device_type": "temperature"
            }
          ]
        }
      ]
    }

Errors
------

Returns error (500) if scan command fails, or if ``board_id`` corresponds to an invalid ``board_id``.

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

``board_id`` : Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of ``board_id`` reserved for future use in OpenDCRE.  IPMI Bridge board has a special ``board_id`` of 40000000.

Request Example
---------------
::

    http://opendcre:5000/opendcre/1.2/version/00000001

Response Schema
---------------

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.2/opendcre-1.2-version",
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

.. code-block:: json

    {
      "api_version": "1.2",
      "firmware_version": "OpenDCRE Emulator v1.2.0",
      "opendcre_version": "1.2.0"
    }

Errors
------

Returns error (500) if version retrieval does not work or if ``board_id`` specifies a nonexistent board.

Read Device
===========

Description
-----------

Read a value from the given ``board_id`` and ``device_id`` for a specific ``device_type``.  The specified ``device_type`` must match the actual physical device type (as reported by the ``scan`` command), and is used to return a translated raw reading value (e.g. temperature in C for a thermistor) based on the existing algorithm for a given sensor type.  The raw value is also returned.

Request Format
--------------
::

    http://<ipaddress>:<port>/opendcre/<version>/read/<device_type>/<board_id>/<device_id>

Parameters
----------

:device_type:  String value (lower-case) indicating what type of device to read
    - ``thermistor``
    - ``temperature``
    - ``humidity``
    - ``led``
    - ``fan_speed``
    - ``pressure`` (not implemented yet)
:board_id: Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of ``board_id`` reserved for future use in OpenDCRE.  IPMI Bridge board has a special ``board_id`` of 40NNNNNN (where NNNNNN is the hex string id of each individual BMC configured with the IPMI Bridge).
:device_id: The device to read on the specified board.  Hexadecimal string representation of a 2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to  OpenDCRE matches the ``device_type`` specified in the command for the given device - else, a 500 error is returned.

Request Example
---------------
::

    http://opendcre:5000/opendcre/1.2/read/thermistor/00000001/0001

Response Schema
---------------

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.2/opendcre-1.2-thermistor-reading",
      "title": "OpenDCRE Thermistor Reading",
      "type": "object",
      "properties": {
        "temperature_c": {
          "type": "number"
        }
      }
    }

Example Response
----------------

.. code-block:: json

    {
      "temperature_c": 19.73
    }

Errors
------

If a device is not readable or does not exist, an error (500) is returned.

Get Asset Information
=====================

Description
-----------

Get asset information from the given ``board_id`` and ``device_id``.  The device's ``device_type`` must be of type ``system`` (as reported by the ``scan`` command), and is used to return asset information for a given device.

Request Format
--------------
::
    
    http://<ipaddress>:<port>/opendcre/<version>/asset/<board_id>/<device_id>

Parameters
----------

:board_id: Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of ``board_id`` reserved for future use in OpenDCRE.  IPMI Bridge board has a special ``board_id`` of 40NNNNNN, where NNNNNN corresponds to the hex string id of each configured BMC.
:device_id: The device to read asset information for on the specified board.  Hexadecimal string representation of a 2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to OpenDCRE is of type ``system`` - else, a 500 error is returned.

Request Example
---------------
::

    http://opendcre:5000/opendcre/1.2/asset/00000001/0004

Response Schema
---------------

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.2/opendcre-1.2-asset-information",
      "title": "OpenDCRE Asset Information",
      "type": "object",
      "properties": {
        "bmc_ip": {
          "type": "string"
        },
        "board_info": {
          "type": "object",
          "properties": {
            "manufacturer": {
              "type": "string"
            },
            "part_number": {
              "type": "string"
            },
            "product_name": {
              "type": "string"
            },
            "serial_number": {
              "type": "string"
            }
          }
        },
        "chassis_info": {
          "type": "object",
          "properties": {
            "chassis_type": {
              "type": "string"
            },
            "part_number": {
              "type": "string"
            },
            "serial_number": {
              "type": "string"
            }
          }
        },
        "product_info": {
          "type": "object",
          "properties": {
            "asset_tag": {
              "type": "string"
            },
            "manufacturer": {
              "type": "string"
            }
            "part_number": {
              "type": "string"
            },
            "product_name": {
              "type": "string"
            },
            "serial_number": {
              "type": "string"
            },
            "version": {
              "type": "string"
            }
          }
        }
      }
    }

Example Response
----------------

.. code-block:: json

    {
      "bmc_ip": "192.168.1.118",
      "board_info": {
        "manufacturer": "Vapor IO",
        "part_number": "0001",
        "product_name": "Example Product",
        "serial_number": "S1234567"
      },
      "chassis_info": {
        "chassis_type": "rack mount chassis",
        "part_number": "P1234567",
        "serial_number": "S1234567"
      },
      "product_info": {
        "asset_tag": "A1234567",
        "manufacturer": "Vapor IO",
        "part_number": "P1234567",
        "product_name": "Example Product",
        "serial_number": S1234567",
        "version": "v1.2.0"
      }
    }

Errors
------

If asset info is unavailable or does not exist, an error (500) is returned.

Power
=====

Description
-----------

Control device power, and/or retrieve its power supply status.

Request Format
--------------
::

    http://<ipaddress>:<port>/opendcre/<version>/power/<board_id>/<device_id>[/<command>]

Parameters
----------

:board_id: Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of ``board_id`` reserved for future use in OpenDCRE.  IPMI Bridge board has a special ``board_id`` of 40NNNNNN, where NNNNNN corresponds to the hex string id of each configured BMC.
:device_id: The device to issue power command to on the specified board.  Hexadecimal string representation of 2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to OpenDCRE is ``power`` - else, a 500 error is returned.
:command: (optional)
    - ``on`` : Turn power on to specified device.
    - ``off`` : Turn power off to specified device.
    - ``cycle`` : Power-cycle the specified device.
    - ``status`` : Get power status for the specified device.

For all commands, power status is returned as the command's response.

Request Example
---------------
::

    http://opendcre:5000/opendcre/1.2/power/00000001/000d/on

Response Schema
---------------

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.2/opendcre-1.2-power-status",
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

.. code-block:: json

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

If a power action fails, or an invalid board/device combination are specified, an error (500) is returned.

Boot Target
===========

Description
-----------

The boot target command may be used to get or set the boot target for a given device (whose device_type must be ``system``).  The boot_target command takes two required parameters - ``board_id`` and ``device_id``, to identify the device to direct the boot_target command to.  Additionally, a third, optional parameter, ``target`` may be used to set the boot target.

Request Format
--------------
::

   http://<ipaddress>:<port>/opendcre/<version>/boot_target/<board_id>/<device_id>[/<target>]

Parameters
----------

:board_id: Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of ``board_id`` reserved for future use in OpenDCRE.  IPMI Bridge board has a special ``board_id`` of 40NNNNNN, where NNNNNN corresponds to the hex string id of each configured BMC.
:device_id: The device to issue boot target command to on the specified board.  Hexadecimal string representation of 2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to OpenDCRE is ``system`` - else, a 500 error is returned.
:target: (optional)
    - ``hdd`` : boot to hard disk
    - ``pxe`` : boot to network
    - ``no_override`` : use the system default boot target

If a target is not specified, boot_target makes no changes, and simply retrieves and returns the system boot target.  If ``target`` is specified and valid, the boot_target command will return the updated boot target value, as provided by the remote device.

Request Example
---------------
::

    http://opendcre:5000/opendcre/1.2/boot_target/00000001/0004


Response Schema
---------------

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.2/opendcre-1.2-boot-target",
      "title": "OpenDCRE Boot Target",
      "type": "object",
      "properties": {
        "target": {
          "type": "string"
        }
      }
    }

Example Response
----------------

.. code-block:: json

    {
      "target": "no_override"
    }

Errors
------

If a boot target action fails, or an invalid board/device combination are specified, an error (500) is returned.

Location
========

Description
-----------

The location command returns the physical location of a given board in the rack, if known, and may also include a given device's position within a chassis (when ``device_id`` is specified).  IPMI boards return ``unknown`` for all fields of ``physical_location`` as location information is not provided by IPMI.

Request Format
--------------
::

   http://<ipaddress>:<port>/opendcre/<version>/location/<board_id>[/<device_id>]

Parameters
----------

:board_id: Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of ``board_id`` reserved for future use in OpenDCRE.  IPMI Bridge board has a special ``board_id`` of 40NNNNNN, where NNNNNN corresponds to the hex string id of each configured BMC.
:device_id: (optional) The device to get location for on the specified board.  Hexadecimal string representation of 2-byte integer value - range 0000..FFFF.  Must be a valid, existing device known to OpenDCRE - else, a 500 error is returned.

Response Schema
---------------

Device Location
    .. code-block:: json

        {
          "$schema": "http://schemas.vapor.io/opendcre/v1.2/opendcre-1.2-device-location",
          "title": "OpenDCRE Device Location",
          "type": "object",
          "properties": {
            "chassis_location": {
              "type": "object",
              "properties": {
                "depth": {
                  "type": "string"
                },
                "horiz_pos": {
                  "type": "string"
                },
                "vert_pos": {
                  "type": "string"
                },
                "server_node": {
                  "type": "string"
                }
              }
            },
            "physical_location": {
              "type": "object",
              "properties": {
                "depth": {
                  "type": "string"
                },
                "horizontal": {
                  "type": "string"
                },
                "vertical": {
                  "type": "string"
                }
              }
            }
          }
        }

Board Location
    .. code-block:: json

        {
          "$schema": "http://schemas.vapor.io/opendcre/v1.2/opendcre-1.2-board-location",
          "title": "OpenDCRE BoardLocation",
          "type": "object",
          "properties": {
            "physical_location": {
              "type": "object",
              "properties": {
                "depth": {
                  "type": "string"
                },
                "horizontal": {
                  "type": "string"
                },
                "vertical": {
                  "type": "string"
                }
              }
            }
          }
        }

Example Responses
-----------------

Device Location
    .. code-block:: json

        {
          "chassis_location": {
            "depth": "unknown",
            "horiz_pos": "unknown",
            "server_node": "unknown",
            "vert_pos": "unknown"
          },
          "physical_location": {
            "depth": "unknown",
            "horizontal": "unknown",
            "vertical": "unknown"
          }
        }

- Valid values for ``chassis_location`` ``depth`` fields are ``front``, ``middle`` and ``rear``.

- Valid values for ``chassis_location`` ``horiz_pos`` fields are ``left``, ``middle`` and ``right``.

- Valid values for ``chassis_location`` ``vert_pos`` fields are ``top``, ``middle``, and ``bottom``.

- ``unknown`` is a valid value for any location field.

Board Location
    .. code-block:: json

        {
          "physical_location": {
            "depth": "unknown",
            "horizontal": "unknown",
            "vertical": "unknown"
          }
        }

- Valid values for ``physical_location`` ``depth`` fields are: ``front``, ``middle``, and ``rear``.

- Valid values for ``physical_location`` ``horizontal`` fields are: ``left``, ``middle``, and ``right``.

- Valid values for ``physical_location`` ``vertical`` fields are: ``top``, ``middle``, and ``bottom``.

- ``unknown`` is a valid value for any location field.

Errors
------

If a location command fails, or an invalid board/device combination are specified, an error (500) is returned.

LED Control
===========

Description
-----------

The LED control command is used to get and set the chassis "identify" LED state.  ``led`` devices known to OpenDCRE allow LED state to be set and retrieved.

Request Format
--------------
::

   http://<ipaddress>:<port>/opendcre/<version>/led/<board_id>/<device_id>[/<led_state>]

Parameters
----------

:board_id: Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of ``board_id`` reserved for future use in OpenDCRE.  IPMI Bridge board has a special ``board_id`` of 40NNNNNN, where NNNNNN corresponds to the hex string id of each configured BMC.
:device_id: The device to issue LED control command to on the specified board.  Hexadecimal string representation of 2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to OpenDCRE is ``led`` - else, a 500 error is returned.
:led_state: (optional)
    - ``on`` : Turn on the chassis identify LED.
    - ``off`` : Turn off the chassis identify LED.

Request Example
---------------
::

    http://opendcre:5000/opendcre/1.2/led/00000001/0005

Response Schema
---------------

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.2/opendcre-1.2-led-control",
      "title": "OpenDCRE LED Control",
      "type": "object",
      "properties": {
        "led_state": {
          "type": "string"
        }
      }
    }

Example Response
----------------

.. code-block:: json

    {
      "led_state": "on"
    }

Errors
------

If a LED control action fails, or an invalid board/device combination are specified, an error (500) is returned.


Fan Speed
=========

Description
-----------

The fan control command is used to get and set the fan speed in RPM for a given fan.  ``fan_speed`` devices known to OpenDCRE that are not IPMI devices allow fan speed to be set and retrieved, while IPMI ``fan_speed`` devices are read-only.

Request Format
--------------
::

   http://<ipaddress>:<port>/opendcre/<version>/fan/<board_id>/<device_id>[/<speed_rpm>]

Parameters
----------

:board_id: Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of ``board_id`` reserved for future use in OpenDCRE.  IPMI Bridge board has a special ``board_id`` of 40NNNNNN, where NNNNNN corresponds to the hex string id of each configured BMC.
:device_id: The device to issue fan control command to on the specified board.  Hexadecimal string representation of 2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to OpenDCRE is ``fan_speed`` - else, a 500 error is returned.
:speed_rpm: (optional) Numeric decimal value to set fan speed to, in range of 0-10000.

- If ``speed_rpm`` is not specified, the ``fan`` command makes no changes, and simply retrieves and returns the fan speed in RPM.  If ``speed_rpm`` is specified and valid, the ``fan`` command will return the updated fan speed value, as provided by the remote device.

Request Example
---------------
::

    http://opendcre:5000/opendcre/1.2/fan/00000001/0002

Response Schema
---------------

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.2/opendcre-1.2-fan-speed",
      "title": "OpenDCRE Fan Speed",
      "type": "object",
      "properties": {
        "speed_rpm": {
          "type": "number"
        }
      }
    }

Example Response
----------------

.. code-block:: json

    {
      "speed_rpm": 4100
    }

Errors
------

If a fan speed action fails, or an invalid board/device combination are specified, an error (500) is returned.

Test
====

Description
-----------

The test command may be used to verify that the OpenDCRE endpoint is up and running, but without attempting to address the device bus.  The command takes no arguments, and if successful, returns a simple status message of "ok".

Request Format
--------------
::

   http://<ipaddress>:<port>/opendcre/<version>/test

Response Schema
---------------

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.2/opendcre-1.2-test-status",
      "title": "OpenDCRE Test Status",
      "type": "object",
      "properties": {
        "status": {
          "type": "string"
        }
      }
    }

Example Response
----------------

.. code-block:: json

    {
      "status": "ok" 
    }

Errors
------

If the endpoint is not running no response will be returned, as the command will always return the response above while the endpoint is functional.
