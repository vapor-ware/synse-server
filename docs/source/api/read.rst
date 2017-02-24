
.. _opendcre-read-command:

read
====

Read a value from the given ``board_id`` and ``device_id`` for a specific ``device_type``.  The specified
``device_type`` must match the actual physical device type (as reported by the :ref:`opendcre-scan-command` command),
and is used to return a translated raw reading value (e.g. temperature in C for a thermistor) based on the existing
algorithm for a given sensor type.


Request
-------

Format
^^^^^^
.. code-block:: none

    GET /opendcre/<version>/read/<device_type>/<rack_id>/<board_id>/<device_id>

Parameters
^^^^^^^^^^

:device_type:
    String value (lower-case) indicating what type of device to read: ``thermistor``, ``temperature``,
    ``humidity``, ``led``, ``fan_speed``, ``pressure``, ``voltage``

:rack_id:
    The id of the rack which the board and device reside on.

:board_id:
    Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of
    ``board_id`` reserved for future use in OpenDCRE.  IPMI Bridge board has a special ``board_id`` of 40NNNNNN
    (where NNNNNN is the hex string id of each individual BMC configured with the IPMI Bridge). For IPMI, the
    ``board_id`` can also be a hostname/ip_address that is associated with the given board.

:device_id:
    The device to read on the specified board.  Hexadecimal string representation of a 2-byte integer
    value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to  OpenDCRE matches
    the ``device_type`` specified in the command for the given device - else, a 500 error is returned. For IPMI, the
    ``device_id`` can also be the value of the ``device_info`` field associated with the given device, if present.

Example
^^^^^^^
.. code-block:: none

    http://opendcre:5000/opendcre/1.3/read/thermistor/00000001/0001

Response
--------

Schema
^^^^^^

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.3/opendcre-1.3-sensor-reading",
      "title": "OpenDCRE Sensor Reading",
      "type": "object",
      "oneOf": [
        {
          "description": "Temperature Readings",
          "properties": {
            "health": {
              "type": "string"
            },
            "states": {
              "type": "array"
            },
            "temperature_c": {
              "type": "number"
            }
          }
        },
        {
          "description": "Thermistor Readings",
          "properties": {
            "health": {
              "type": "string"
            },
            "states": {
              "type": "array"
            },
            "temperature_c": {
              "type": "number"
            }
          }
        },
        {
          "description": "Fan Speed Readings",
          "properties": {
            "health": {
              "type": "string"
            },
            "states": {
              "type": "array"
            },
            "speed_rpm": {
              "type": "number"
            }
          }
        },
        {
          "description": "LED Readings",
          "properties": {
            "health": {
              "type": "string"
            },
            "states": {
              "type": "array"
            },
            "led_state": {
              "type": "string",
              "enum": [
                "on",
                "off"
              ]
            }
          }
        },
        {
          "description": "Pressure Readings",
          "properties": {
            "health": {
              "type": "string"
            },
            "states": {
              "type": "array"
            },
            "pressure_kpa": {
              "type": "number"
            }
          }
        },
        {
          "description": "Voltage Readings",
          "properties": {
            "health": {
              "type": "string"
            },
            "states": {
              "type": "array"
            },
            "voltage": {
              "type": "number"
            }
          }
        }
      ]
    }

Example
^^^^^^^

.. code-block:: json

    {
      "health": "ok",
      "states": [],
      "temperature_c": 19.73
    }

Errors
^^^^^^

:500:
    - the device is not readable or does not exist
    - specified device is not of the specified device type
    - invalid/nonexistent ``board_id`` or ``device_id``