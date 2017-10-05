
.. _synse-server-scan-command:

scan
====

The ``scan`` command polls boards and devices attached to the board. There are primarily two ways that scan
operates -- "scan all", and "scan entity", where an entity could be a rack or a board. When performing a
"scan all" command, if a scan cache does not exist, it will scan the physical boards and devices. If a scan
cache does exist, it will use the results from the cache. To refresh the scan cache, the "force scan" command
should be used.

.. note::
    It is likely a good idea for applications to scan for all boards on startup, to ensure a proper map of boards
    and devices is available to the application. Mismatches of board and device types and identifiers will result
    in 500 errors being returned for various commands that rely on these values mapping to actual hardware.

Request
-------

Format
^^^^^^

:scan all:
    .. code-block:: none

        GET /synse/<version>/scan

:force scan:
    .. code-block:: none

        GET /synse/<version>/scan/force

:scan rack:
    .. code-block:: none

        GET /synse/<version>/<rack_id>

:scan board:
    .. code-block:: none

        GET /synse/<version>/<rack_id></board_id>


Parameters
^^^^^^^^^^

:force:
    *(optional)* A flag which, when present, will force the re-scan of all racks, boards, and devices.
    This parameter is only associated with "scan all" behavior and does not apply to scans at a rack
    or board level. Forcing a scan re-scans the devices and updates the scan cache.

:rack_id:
    *(optional)* The id of the rack to scan, if only the rack is specified. If the rack is specified with
    a board id, this is the rack where the target board resides.

:board_id:
    *(optional)* Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper
    byte of ``board_id`` reserved for future use in Synse Server.  IPMI Bridge boards have a special ``board_id`` of
    40NNNNNN (where NNNNNN is the hex string id of each configured BMC). For IPMI, the ``board_id`` can also be
    a hostname/ip_address that is associated with the given board.

Example
^^^^^^^
.. code-block:: none

    GET http://<host>:5000/synse/1.4/scan
    GET http://<host>:5000/synse/1.4/scan/force
    GET http://<host>:5000/synse/1.4/scan/rack_1
    GET http://<host>:5000/synse/1.4/scan/rack_1/00000001

Response
--------

Schema
^^^^^^

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/synse/v1.4/synse-1.4-boards-devices",
      "title": "Synse Server Boards and Devices",
      "type": "object",
      "properties": {
        "racks": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "rack_id": {
                "type": "string"
              },
              "boards": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "board_id": {
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
                              "pressure",
                              "voltage",
                              "power_supply"
                            ]
                          }
                        }
                      }
                    },
                    "hostnames": {
                      "type": "array",
                      "items": {
                        "type": "string"
                      }
                    },
                    "ip_addresses": {
                      "type": "array",
                      "items": {
                        "type": "string"
                      }
                    },
                  }
                }
              }
            }
          }
        }
      }
    }


Example
^^^^^^^

.. code-block:: json

    {
      "racks": [
        {
          "boards": [
            {
              "board_id": "00000001",
              "devices": [
                {
                  "device_id": "0001",
                  "device_type": "system"
                },
                {
                  "device_id": "0002",
                  "device_type": "fan_speed"
                },
                {
                  "device_id": "0003",
                  "device_type": "fan_speed"
                },
                {
                  "device_id": "0004",
                  "device_type": "power"
                },
                {
                  "device_id": "0005",
                  "device_type": "led"
                },
                {
                  "device_id": "2000",
                  "device_type": "temperature"
                },
                {
                  "device_id": "4000",
                  "device_type": "temperature"
                }
              ],
              "hostnames": [
                "kafka001.vapor.io"
              ],
              "ip_addresses": [
                "192.168.1.10"
              ]
            }
          ],
          "rack_id": "rack_1"
        }
      ]
    }

Errors
^^^^^^

:500:
    - the scan command fails
    - invalid/nonexistent ``board_id``
