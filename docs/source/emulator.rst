=================
OpenDCRE Emulator
=================

Emulator Configuration
----------------------

In the absence of HAT hardware, OpenDCRE can utilize a software emulator to simulate and test various capabilities of OpenDCRE.  The OpenDCRE emulator is configured by means of a JSON file (the default file is ``simple.json``) which is stored in the ``/opendcre/opendcre_southbound`` directory of the OpenDCRE Docker container.

To modify the emulator output, users may clone the `OpenDCRE GitHub repository`__, and change the contents of ``simple.json``, then rebuild the OpenDCRE container.

.. _OpenDCRE: https://github.com/vapor-ware/OpenDCRE

__ OpenDCRE_

Example emulator configuration from ``simple.json`` is below, followed by an explanation of the contents.
.. code-block:: json

    {
      "boards": [
        {
          "board_id": "00000001",
          "firmware_version" : "OpenDCRE Emulator v1.2.0 - Standalone Server",
          "devices" : [
            {
              "device_id": "0001",
              "device_type": "thermistor",
              "read":
                {
                  "repeatable": true,
                  "responses": [
                    656,
                    646,
                    636,
                    625,
                    615,
                    605,
                    594,
                    584,
                    573,
                    563,
                    553,
                    542,
                    532,
                    522,
                    512,
                    502,
                    491,
                    482,
                    472,
                    462,
                    452
                  ]
                }
            },
            {
              "device_id": "0002",
              "device_type": "fan_speed",
              "read":
                {
                  "repeatable": true,
                  "responses": [
                    4100,
                    4100,
                    4000,
                    4000,
                    3900,
                    3900,
                    3800,
                    3800,
                    3700,
                    3700,
                    3800,
                    3800,
                    3900,
                    3900,
                    4000,
                    4000,
                    4100,
                    4100,
                    4200,
                    4200
                  ]
                },
              "write":
                {
                  "repeatable": true,
                  "responses": [
                    "W1"
                  ]
                }
            },
            {
              "device_id": "0004",
              "device_type": "system",
              "asset_info":
              {
                  "repeatable": true,
                  "responses": [
                    "not yet implemented"
                  ]
              },
              "boot_target": {
                  "repeatable": true,
                  "responses": [
                    "not yet implemented"
                  ]
              }
            },
            {
              "device_id": "0005",
              "device_type": "led",
              "read":
                {
                  "repeatable": true,
                  "responses": [
                    1,
                    0
                  ]
                },
              "write":
                {
                  "repeatable": true,
                  "responses": [
                    "W1"
                  ]
                }
            },
            {
              "device_id": "0009",
              "device_type": "thermistor",
              "read":
                {
                  "repeatable": true,
                  "responses": [
                    656,
                    646,
                    636,
                    625,
                    615,
                    605,
                    594,
                    584,
                    573,
                    563,
                    553,
                    542,
                    532,
                    522,
                    512,
                    502,
                    491,
                    482,
                    472,
                    462,
                    452
                  ]
                }
            },
            {
              "device_id": "2000",
              "device_type": "temperature",
              "read":
                {
                  "repeatable": true,
                  "responses": [
                    28.78,
                    29.77,
                    30.75,
                    31.84,
                    32.82,
                    33.81,
                    34.89,
                    35.88,
                    36.96,
                    37.94,
                    38.93,
                    40.21,
                    41.27,
                    42.33,
                    43.39,
                    44.45,
                    45.61,
                    46.57,
                    47.63,
                    48.69,
                    49.75
                  ]
                }
            },
            {
              "device_id": "4000",
              "device_type": "temperature",
              "read":
                {
                  "repeatable": true,
                  "responses": [
                    28.78,
                    29.77,
                    30.75,
                    31.84,
                    32.82,
                    33.81,
                    34.89,
                    35.88,
                    36.96,
                    37.94,
                    38.93,
                    40.21,
                    41.27,
                    42.33,
                    43.39,
                    44.45,
                    45.61,
                    46.57,
                    47.63,
                    48.69,
                    49.75
                  ]
                }
            },
            {
              "device_id": "000D",
              "device_type": "power",
              "power":
                {
                  "repeatable": true,
                  "responses": [
                    "0,0,0,0"
                  ]
                }
            }
          ]
        },
        {
          "board_id": "00000002",
          "firmware_version" : "OpenDCRE Emulator v1.2.0 - Microserver",
          "devices" : [
            {
              "device_id": "0002",
              "device_type": "fan_speed",
              "read":
                {
                  "repeatable": true,
                  "responses": [
                    4100,
                    4100,
                    4000,
                    4000,
                    3900,
                    3900,
                    3800,
                    3800,
                    3700,
                    3700,
                    3800,
                    3800,
                    3900,
                    3900,
                    4000,
                    4000,
                    4100,
                    4100,
                    4200,
                    4200
                  ]
                },
              "write":
                {
                  "repeatable": true,
                  "responses": [
                    "W1"
                  ]
                }
            },
            {
              "device_id": "8001",
              "device_type": "system",
              "asset_info":
              {
                  "repeatable": true,
                  "responses": [
                    "not yet implemented"
                  ]
              },
              "boot_target": {
                  "repeatable": true,
                  "responses": [
                    "not yet implemented"
                  ]
              }
            },
            {
              "device_id": "8002",
              "device_type": "power",
              "power":
                {
                  "repeatable": true,
                  "responses": [
                    "0,0,0,0"
                  ]
                }
            },
            {
              "device_id": "8003",
              "device_type": "temperature",
              "read":
                {
                  "repeatable": true,
                  "responses": [
                    28.78,
                    29.77,
                    30.75,
                    31.84,
                    32.82,
                    33.81,
                    34.89,
                    35.88,
                    36.96,
                    37.94,
                    38.93,
                    40.21,
                    41.27,
                    42.33,
                    43.39,
                    44.45,
                    45.61,
                    46.57,
                    47.63,
                    48.69,
                    49.75
                  ]
                }
            },
            {
              "device_id": "8101",
              "device_type": "system",
              "asset_info":
              {
                  "repeatable": true,
                  "responses": [
                    "not yet implemented"
                  ]
              },
              "boot_target": {
                  "repeatable": true,
                  "responses": [
                    "not yet implemented"
                  ]
              }
            },
            {
              "device_id": "8102",
              "device_type": "power",
              "power":
                {
                  "repeatable": true,
                  "responses": [
                    "0,0,0,0"
                  ]
                }
            },
            {
              "device_id": "8103",
              "device_type": "temperature",
              "read":
                {
                  "repeatable": true,
                  "responses": [
                    28.78,
                    29.77,
                    30.75,
                    31.84,
                    32.82,
                    33.81,
                    34.89,
                    35.88,
                    36.96,
                    37.94,
                    38.93,
                    40.21,
                    41.27,
                    42.33,
                    43.39,
                    44.45,
                    45.61,
                    46.57,
                    47.63,
                    48.69,
                    49.75
                  ]
                }
            },
            {
              "device_id": "8201",
              "device_type": "system",
              "asset_info":
              {
                  "repeatable": true,
                  "responses": [
                    "not yet implemented"
                  ]
              },
              "boot_target": {
                  "repeatable": true,
                  "responses": [
                    "not yet implemented"
                  ]
              }
            },
            {
              "device_id": "8202",
              "device_type": "power",
              "power":
                {
                  "repeatable": true,
                  "responses": [
                    "0,0,0,0"
                  ]
                }
            },
            {
              "device_id": "8203",
              "device_type": "temperature",
              "read":
                {
                  "repeatable": true,
                  "responses": [
                    28.78,
                    29.77,
                    30.75,
                    31.84,
                    32.82,
                    33.81,
                    34.89,
                    35.88,
                    36.96,
                    37.94,
                    38.93,
                    40.21,
                    41.27,
                    42.33,
                    43.39,
                    44.45,
                    45.61,
                    46.57,
                    47.63,
                    48.69,
                    49.75
                  ]
                }
            },
            {
              "device_id": "8301",
              "device_type": "system",
              "asset_info":
              {
                  "repeatable": true,
                  "responses": [
                    "not yet implemented"
                  ]
              },
              "boot_target": {
                  "repeatable": true,
                  "responses": [
                    "not yet implemented"
                  ]
              }
            },
            {
              "device_id": "8302",
              "device_type": "power",
              "power":
                {
                  "repeatable": true,
                  "responses": [
                    "0,0,0,0"
                  ]
                }
            },
            {
              "device_id": "8303",
              "device_type": "temperature",
              "read":
                {
                  "repeatable": true,
                  "responses": [
                    28.78,
                    29.77,
                    30.75,
                    31.84,
                    32.82,
                    33.81,
                    34.89,
                    35.88,
                    36.96,
                    37.94,
                    38.93,
                    40.21,
                    41.27,
                    42.33,
                    43.39,
                    44.45,
                    45.61,
                    46.57,
                    47.63,
                    48.69,
                    49.75
                  ]
                }
            },
            {
              "device_id": "0005",
              "device_type": "led",
              "read":
                {
                  "repeatable": true,
                  "responses": [
                    1,
                    0
                  ]
                },
              "write":
                {
                  "repeatable": true,
                  "responses": [
                    "W1"
                  ]
                }
            },
            {
              "device_id": "2000",
              "device_type": "temperature",
              "read":
                {
                  "repeatable": true,
                  "responses": [
                    28.78,
                    29.77,
                    30.75,
                    31.84,
                    32.82,
                    33.81,
                    34.89,
                    35.88,
                    36.96,
                    37.94,
                    38.93,
                    40.21,
                    41.27,
                    42.33,
                    43.39,
                    44.45,
                    45.61,
                    46.57,
                    47.63,
                    48.69,
                    49.75
                  ]
                }
            },
            {
              "device_id": "4000",
              "device_type": "temperature",
              "read":
                {
                  "repeatable": true,
                  "responses": [
                    28.78,
                    29.77,
                    30.75,
                    31.84,
                    32.82,
                    33.81,
                    34.89,
                    35.88,
                    36.96,
                    37.94,
                    38.93,
                    40.21,
                    41.27,
                    42.33,
                    43.39,
                    44.45,
                    45.61,
                    46.57,
                    47.63,
                    48.69,
                    49.75
                  ]
                }
            },
            {
              "device_id": "000D",
              "device_type": "power",
              "power":
                {
                  "repeatable": true,
                  "responses": [
                    "0,0,0,0"
                  ]
                }
            }
          ]
        }
      ]
    }

The OpenDCRE emulator simulates two different boards (servers) - the first being a single-node server, and the second a multi-node (microserver).  The JSON document file is structured around a collection of boards and devices.

Boards
------

Each board must have a ``board_id`` and ``firmware_version`` field.  Each ``board_id`` must be a unique 4-byte value, encoded as a hex string between "00000000" and "00FFFFFF" (the upper byte is reserved, and must always be 00), and ``firmware_version`` must be a string value (including empty string).

The ``board_id`` is used in the OpenDCRE API to address a given board, while the ``firmware_version`` field is used to populate the ``firmware_version`` field of the response to the OpenDCRE "version" command for a given board (e.g.
::

    http://<ipaddress>:5000/opendcre/1.2/version/1

gets the version information for board 1).

As with all commands in OpenDCRE, if a board or device does not exist in the emulator configuration, then a 500 error is returned as the result of a given command.

Devices
-------

A given board also has a collection of devices.  Each device is identified by a ``device_id``, used to indicate a given device in an OpenDCRE command - e.g.:
::

    http://<ipaddress>:5000/opendcre/1.2/read/thermistor/00000001/0001

The ``device_id`` field is a 2-byte value represented as a hexadecimal string that is unique to a given board.

Device Types
------------

The ``device_type`` field must be present, and must contain a string value that corresponds to an OpenDCRE-supported device type.  This list includes:

- ``thermistor``
- ``power``
- ``humidity``
- ``pressure`` (not implemented)
- ``led``
- ``system``
- ``fan_speed``
- ``temperature``

.. versionchanged:: 1.2
    In previous releases, a device type of ``none`` indicated that no device is present at a given ``device_id`` on the given board, and may be ignored.  In OpenDCRE v1.2 the ``none`` device type has been removed.

Other device types (e.g. for additional sensors and actions) will be added in future revisions of OpenDCRE, or may be added by developers wishing to add support for other device types.

Finally, a field corresponding to the action supported for a given device type is required.  A map of device types to supported actions is below:

=============== ==============================================
Device Type     Action Supported
--------------- ----------------------------------------------
``thermistor``  ``read``
``temperature`` ``read``
``power``       ``power``
``humidity``    ``read``
``pressure``    not supported yet
``led``         ``read``, ``write``
``fan_speed``   ``read``, ``write``
``system``      not supported yet
=============== ==============================================

Read
----

For the ``read`` action's field in the OpenDCRE emulator configuration, two fields may be configured relating to the responses returned from a read command for the given device.

First, the ``repeatable`` field may be set to true or false, depending on whether it is desirable for the list of responses set in the responses field to repeat in a round-robin fashion, or if a device should stop returning data after its response list has been exhausted.

The ``responses`` field is a list of zero or more values that may be returned for a given read command.  The raw values are converted (where necessary) by the built-in OpenDCRE conversion functions, based on the given ``device_type``.  Some examples are given for the thermistor sensor device type in the ``simple.json`` file.

When a list of values is provided for responses, the emulator iterates sequentially through the items in that list, until the list is exhausted (if repeatable is set to "true", then the emulator returns to the beginning of the list).

An empty responses list means the device returns no data, which translates to a 500 error for the read command at the OpenDCRE REST API level (useful for simulating errors).  To always return the same single value, a responses list with a single element, and repeatable set to "true" will suffice.

Read Response Format
~~~~~~~~~~~~~~~~~~~~

The table below describes the response format for each device type for ``read`` commands to the emulator.

=============== ==============================================
Device Type     Format
--------------- ----------------------------------------------
``thermistor``  integer, converted by OpenDCRE (see ``simple.json``)
``temperature`` numeric, sent back as numeric value (e.g. 28.78)
``humidity``    numeric, converted by OpenDCRE
``led``         integer, ``1`` is ``on`` and ``0`` is ``off``; all other values are errors
``fan_speed``   integer, sent back as integer value (e.g. 4100)
=============== ==============================================

Values that do not conform to the above formats will result in errors to ``read`` requests made to the emulator, as they would on the device bus.

Write
-----

For the ``write`` action's field in the OpenDCRE emulator configuration, two fields may be configured, relating to the responses returned from a write command for the given device.  The fields are laid out and function in the same manner as ``read`` fields.

Write Response Format
~~~~~~~~~~~~~~~~~~~~~

The table below describes the response format for each device type for ``write`` commands to the emulator.

=============== ==============================================
Device Type     Format
--------------- ----------------------------------------------
``led``         string - ``W1`` is successful, while ``W0`` is unsuccessful; all other values are errors.
``fan_speed``   string - ``W1`` is successful, while ``W0`` is unsuccessful; all other values are errors.
=============== ==============================================

Values that do not conform to the above formats will result in errors to ``write`` requests made to the emulator, as they would on the device bus.

Writing to a device from OpenDCRE to the emulator does not currently result in any state change for a corresponding device in the emulator. That functionality may be added in a future release.

Power
-----

For the ``power`` action's field in the OpenDCRE emulator configuration, similar fields are present - repeatable and responses.

For every power command (e.g. ``on``/``off``/``cycle``/``status``) issued to a power device in the OpenDCRE emulator, a response is returned from the responses list, which may be repeatable or non-repeatable.  The values in the responses list correspond to power status values returned over PMBUS from the hot swap controller on an OCP server, and are expressed as an integer value in the emulator configuration (see example above).  OpenDCRE converts the raw response to a friendly power status result using its built-in conversion functions.

Other Notes
-----------

The emulator configuration in ``simple.json`` is designed to provide a simple view and demonstration of how OpenDCRE works.  The OpenDCRE emulator is also used for testing purposes, and additional emulator configurations may be found under the ``/opendcre/opendcre_southbound/tests/data`` directory of the OpenDCRE Docker container.

An invalid emulator configuration will cause the OpenDCRE emulator to fail to start or function properly.

Additional features of the emulator that may be used by advanced users or hardware/protocol developers include:
    - Ability to send back raw bytes for responses to ``scan``, ``version``, ``read``, ``write``, and ``power`` commands.  In tests, this can be seen where a list (or list of lists) of integer values is specified for a given response. Special sentinel values (999, 10xx) are used to place sequence numbers and checksums into the packet stream.
    - Ability to support command retries in cases of invalid packets, line noise, etc.
    - Ability to support 'scan-all' command and retries using time-division multiplexing; success and failure scenarios may be implemented for various configurations.  See the ``test-scanall`` tests.
    - IPMI emulator support is not yet included, but may be in a future release.