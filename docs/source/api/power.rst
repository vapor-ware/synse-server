
.. _synse-server-power-command:

power
=====

Control device power, and/or retrieve its power supply status. The specified device's ``device_type`` must be of
type ``power`` (as reported by the :ref:`synse-server-scan-command` command).


Request
-------

Format
^^^^^^
.. code-block:: none

    GET /synse/<version>/power/<rack_id>/<board_id>/<device_id>[/<command>]

Parameters
^^^^^^^^^^

:rack_id:
    The id of the rack which the specified board and device reside on.

:board_id:
    Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of
    ``board_id`` reserved for future use in Synse Server.  IPMI Bridge board has a special ``board_id`` of 40NNNNNN,
    where NNNNNN corresponds to the hex string id of each configured BMC. For IPMI, the ``board_id`` can also be
    a hostname/ip_address that is associated with the given board.

:device_id:
    The device to issue power command to on the specified board.  Hexadecimal string representation of 2-byte
    integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to Synse Server
    is ``power`` - else, a 500 error is returned. For IPMI, the ``device_id`` can also be the
    value of the ``device_info`` field associated with the given device, if present.

:command:
    *(optional)* The power command to issue. Valid commands are:

    - ``on`` : Turn power on to specified device
    - ``off`` : Turn power off to specified device
    - ``cycle`` : Power-cycle the specified device
    - ``status`` : Get power status for the specified device

For all commands, power status is returned as the command's response.

Example
^^^^^^^
.. code-block:: none

    http://<host>:5000/synse/1.4/power/00000001/000d/on

Response
--------

Schema
^^^^^^

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/synse/v1.4/synse-1.4-power-status",
      "title": "Synse Server Power Status",
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
          "type": "string",
          "enum": [
            "on",
            "off"
          ]
        },
        "under_voltage": {
          "type": "boolean"
        }
      }
    }

Example
^^^^^^^

.. code-block:: json

    {
      "input_power": 198.57686579513486,
      "input_voltage": 12.500651075576853,
      "output_current": 15.879801734820322,
      "over_current": false,
      "pmbus_raw": "0,12000,2400,3356",
      "power_ok": true,
      "power_status": "on",
      "under_voltage": false
    }

Errors
^^^^^^

:500:
    - power action fails
    - the specified device is not of type ``power``
    - invalid/nonexistent ``board_id`` or ``device_id``