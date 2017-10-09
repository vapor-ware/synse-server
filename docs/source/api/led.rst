
.. _synse-server-led-command:

LED
===

The LED control command is used to get and set the chassis "identify" LED state. ``led`` devices known to
Synse Server allow LED state to be set and retrieved.

Request
-------

Format
^^^^^^
.. code-block:: none

   GET /synse/<version>/led/<rack_id>/<board_id>/<device_id>[/<state>[/<color>/<blink_state>]]

Parameters
^^^^^^^^^^

:rack_id:
    The id of the rack upon which the specified board and device reside.

:board_id:
    Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of
    ``board_id`` reserved for future use in Synse Server.  IPMI Bridge board has a special ``board_id`` of 40NNNNNN, where
    NNNNNN corresponds to the hex string id of each configured BMC. For IPMI, the ``board_id`` can also be
    a hostname/ip_address that is associated with the given board.

:device_id:
    The device to issue LED control command to on the specified board.  Hexadecimal string representation of
    2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to
    Synse Server is ``led`` - else, a 500 error is returned. For IPMI, the ``device_id`` can also be the
    value of the ``device_info`` field associated with the given device, if present.

:state:
    *(optional)* The LED state to set. Valid values include:

    - ``on`` : Turn on the chassis identify LED
    - ``off`` : Turn off the chassis identify LED

:color:
    *(optional)* 3-byte numeric hex (base-16) string corresponding to RGB LED color. For example, "ffffff" is white,
    "ff0000" is red, etc.

:blink_state:
    *(optional)* Sets the blink state of the LED. Valid values include:

    - ``blink`` : Sets the LED to blink
    - ``steady`` : Indicates that the LED should remain on without blinking


Example
^^^^^^^
.. code-block:: none

    http://<host>:5000/synse/1.4/led/00000001/0005

Response
--------

Schema
^^^^^^

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/synse/v1.4/synse-1.4-led-control",
      "title": "Synse Server LED Control",
      "type": "object",
      "properties": {
        "led_state": {
          "type": "string",
          "enum": [
            "on",
            "off"
          ]
        }
      }
    }

Example
^^^^^^^

.. code-block:: json

    {
      "led_state": "on"
    }

Errors
^^^^^^

:500:
    - LED control action fails
    - specified device is not of type ``led``
    - invalid ``board_id`` or ``device_id``
