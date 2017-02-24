
.. _opendcre-led-command:

LED
===

The LED control command is used to get and set the chassis "identify" LED state. ``led`` devices known to OpenDCRE
allow LED state to be set and retrieved.

Request
-------

Format
^^^^^^
.. code-block:: none

   GET /opendcre/<version>/led/<rack_id>/<board_id>/<device_id>[/<led_state>]

Parameters
^^^^^^^^^^

:rack_id:
    The id of the rack upon which the specified board and device reside.

:board_id:
    Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of
    ``board_id`` reserved for future use in OpenDCRE.  IPMI Bridge board has a special ``board_id`` of 40NNNNNN, where
    NNNNNN corresponds to the hex string id of each configured BMC. For IPMI, the ``board_id`` can also be
    a hostname/ip_address that is associated with the given board.

:device_id:
    The device to issue LED control command to on the specified board.  Hexadecimal string representation of
    2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to
    OpenDCRE is ``led`` - else, a 500 error is returned. For IPMI, the ``device_id`` can also be the
    value of the ``device_info`` field associated with the given device, if present.

:led_state:
    *(optional)* The LED state to set. Valid values include:

    - ``on`` : Turn on the chassis identify LED
    - ``off`` : Turn off the chassis identify LED

Example
^^^^^^^
.. code-block:: none

    http://opendcre:5000/opendcre/1.3/led/00000001/0005

Response
--------

Schema
^^^^^^

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.3/opendcre-1.3-led-control",
      "title": "OpenDCRE LED Control",
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
