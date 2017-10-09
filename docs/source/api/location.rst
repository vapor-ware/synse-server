
.. _synse-server-location-command:

location
========

The location command returns the physical location of a given board in the rack, if known, and may also include
a given device's position within a chassis (when the ``device_id`` parameter is specified).  IPMI boards return
``unknown`` for all fields of ``physical_location`` as location information is not provided by IPMI.

Request
-------

Format
^^^^^^
.. code-block:: none

   GET /synse/<version>/location/<rack_id>/<board_id>[/<device_id>]

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
    *(optional)* The device to get location for on the specified board. Hexadecimal string representation of
    2-byte integer value - range 0000..FFFF.  Must be a valid, existing device known to Synse Server - else, a 500
    error is returned. For IPMI, the ``device_id`` can also be the value of the ``device_info`` field associated
    with the given device, if present.


Response
--------

Schema
^^^^^^

Device Location
"""""""""""""""

    .. code-block:: json

        {
          "$schema": "http://schemas.vapor.io/synse/v1.4/synse-1.4-device-location",
          "title": "Synse Server Device Location",
          "type": "object",
          "properties": {
            "chassis_location": {
              "type": "object",
              "properties": {
                "depth": {
                  "type": "string",
                  "enum": [
                    "unknown",
                    "front",
                    "middle",
                    "rear"
                  ]
                },
                "horiz_pos": {
                  "type": "string",
                  "enum": [
                    "unknown",
                    "left",
                    "middle",
                    "right"
                  ]
                },
                "vert_pos": {
                  "type": "string",
                  "enum": [
                    "unknown",
                    "top",
                    "middle",
                    "bottom"
                  ]
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
                  "type": "string",
                  "enum": [
                    "unknown",
                    "front",
                    "middle",
                    "rear"
                  ]
                },
                "horizontal": {
                  "type": "string",
                  "enum": [
                    "unknown",
                    "left",
                    "middle",
                    "right"
                  ]
                },
                "vertical": {
                  "type": "string",
                  "enum": [
                    "unknown",
                    "top",
                    "middle",
                    "bottom"
                  ]
                }
              }
            }
          }
        }


Board Location
""""""""""""""

    .. code-block:: json

        {
          "$schema": "http://schemas.vapor.io/synse/v1.4/synse-1.4-board-location",
          "title": "Synse Server Board Location",
          "type": "object",
          "properties": {
            "physical_location": {
              "type": "object",
              "properties": {
                "depth": {
                  "type": "string",
                  "enum": [
                    "unknown",
                    "front",
                    "middle",
                    "rear"
                  ]
                },
                "horizontal": {
                  "type": "string",
                  "enum": [
                    "unknown",
                    "left",
                    "middle",
                    "right"
                  ]
                },
                "vertical": {
                  "type": "string",
                  "enum": [
                    "unknown",
                    "top",
                    "middle",
                    "bottom"
                  ]
                }
              }
            }
          }
        }

Example
^^^^^^^

Device Location
"""""""""""""""

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

Board Location
""""""""""""""

    .. code-block:: json

        {
          "physical_location": {
            "depth": "unknown",
            "horizontal": "unknown",
            "vertical": "unknown"
          }
        }

Errors
^^^^^^

:500:
    - location command fails
    - invalid/nonexistent ``board_id`` or ``device_id``
