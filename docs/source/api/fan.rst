
.. _synse-server-fan-command:

fan
===

The fan control command is used to get the fan speed (in RPM) for a given fan.

Request
-------

Format
^^^^^^
.. code-block:: none

   GET /synse/<version>/fan/<rack_id>/<board_id>/<device_id>[/<speed_rpm>]

Parameters
^^^^^^^^^^

:rack_id:
    The id of the rack upon which the specified board and device reside.

:board_id:
    Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of
    ``board_id`` reserved for future use in Synse Server.  IPMI Bridge board has a special ``board_id`` of 40NNNNNN,
    where NNNNNN corresponds to the hex string id of each configured BMC. For IPMI, the ``board_id`` can also be
    a hostname/ip_address that is associated with the given board.

:device_id:
    The device to issue fan control command to on the specified board.  Hexadecimal string representation of
    2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to
    Synse Server is ``fan_speed`` - else, a 500 error is returned. For IPMI, the ``device_id`` can also be the
    value of the ``device_info`` field associated with the given device, if present.

:speed_rpm:
    *(optional)* Numeric decimal value to set fan speed to.

    .. note::
        IPMI devices do not yet support the setting of fan speed, so this parameter can be ignored for
        all IPMI setups.


Example
^^^^^^^
.. code-block:: none

    http://<host>:5000/synse/1.4/fan/00000001/0002

Response
--------

Schema
^^^^^^

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/synse/v1.4/synse-1.4-fan-speed",
      "title": "Synse Server Fan Speed",
      "type": "object",
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
    }

Example
^^^^^^^

.. code-block:: json

    {
      "health": "ok",
      "speed_rpm": 4100.0,
      "states": []
    }

Errors
^^^^^^

:500:
    - fan speed action fails
    - specified device is not a fan device
    - invalid/nonexistent ``board_id`` or ``device_id``


