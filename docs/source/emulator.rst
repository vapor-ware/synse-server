=================
OpenDCRE Emulator
=================

Emulator Configuration
----------------------

In the absence of HAT hardware, OpenDCRE automatically switches to using a software emulator, to simulate various capabilities of OpenDCRE.  The OpenDCRE emulator is configured by means of a JSON file (the default file is ``simple.json``) which is stored in the ``/opendcre/opendcre_southbound`` directory of the OpenDCRE Docker container.

To modify the emulator output, users may clone the `OpenDCRE GitHub repository`__, and change the contents of ``simple.json``, then rebuild the OpenDCRE container.

.. _OpenDCRE: https://github.com/vapor-ware/OpenDCRE

__ OpenDCRE_

Example emulator configuration from ``simple.json`` is below, followed by an explanation of the contents.
::

    {
      "boards": [
        {
          "board_id": "00000001",
          "firmware_version" : "OpenDCRE Emulator v1.1.0",
          "devices" : [
            {
              "device_id": "01ff",
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
              "device_id": "02ff",
              "device_type": "none",
              "read":
                {
                  "repeatable": true,
                  "responses": [ ]
                }
            },
            {
              "device_id": "03ff",
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
              "device_id": "04ff",
              "device_type": "none",
              "read":
                {
                  "repeatable": true,
                  "responses": [ ]
                }
            },
            {
              "device_id": "05ff",
              "device_type": "none",
              "read":
                {
                  "repeatable": true,
                  "responses": [ ]
                }
            },
            {
              "device_id": "06ff",
              "device_type": "none",
              "read":
                {
                  "repeatable": true,
                  "responses": [ ]
                }
            },
            {
              "device_id": "07ff",
              "device_type": "none",
              "read":
                {
                  "repeatable": true,
                  "responses": [ ]
                }
            },
            {
              "device_id": "08ff",
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
              "device_id": "09ff",
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
              "device_id": "0aff",
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
              "device_id": "0bff",
              "device_type": "none",
              "read":
                {
                  "repeatable": true,
                  "responses": [ ]
                }
            },
            {
              "device_id": "0cff",
              "device_type": "none",
              "read":
                {
                  "repeatable": true,
                  "responses": [ ]
                }
            },
            {
              "device_id": "0dff",
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

The OpenDCRE emulator simulates a single OpenDCRE HAT board with 13 devices.  The JSON document file is structured around a collection of boards and devices.

Boards
------

Each board must have a ``board_id`` and ``firmware_version`` field.  Each ``board_id`` must be a unique 4-byte value, encoded as a hex string between "00000000" and "00FFFFFF" (the upper byte is reserved, and must always be 00), and ``firmware_version`` must be a string value (including empty string).

The ``board_id`` is used in the OpenDCRE API to address a given board, while the ``firmware_version`` field is used to populate the ``firmware_version`` field of the response to the OpenDCRE "version" command for a given board (e.g.
::

    http://<ipaddress>:5000/opendcre/1.1/version/1

gets the version information for board 1).

As with all commands in OpenDCRE, if a board or device does not exist in the emulator configuration, then a 500 error is returned as the result of a given command.

Devices
-------

A given board also has a collection of devices.  Each device is identified by a ``device_id``, used to indicate a given device in an OpenDCRE command - e.g.:
::

    http://<ipaddress>:5000/opendcre/1.1/read/thermistor/00000001/01ff

The ``device_id`` field is a 2-byte value represented as a hexadecimal string that is unique to a given board.

Device Types
------------

The ``device_type`` field must be present, and must contain a string value that corresponds to an OpenDCRE-supported device type.  This list includes:

- ``thermistor``
- ``power``
- ``humidity``
- ``pressure``
- ``led``
- ``ipmb``
- ``door_lock``
- ``current``
- ``temperature``
- ``none``

A device type of ``none`` indicates that no device is present at a given ``device_id`` on the given board, and may be ignored.

Other device types (e.g. for additional sensors and actions) will be added in future revisions of OpenDCRE, or may be added by developers wishing to add support for other device types.

Finally, a field corresponding to the action supported for a given device type is required.  A map of device types to supported actions is below:

=============== ==============================================
Device Type     Action Supported
--------------- ----------------------------------------------
``thermistor``  ``read``
``power``       ``power``
``humidity``    ``read``
``pressure``    none (may be added in future OpenDCRE release)
``led``            none (may be added in future OpenDCRE release)
``ipmb``        none (may be added in future OpenDCRE release)
``door_lock``   none (may be added in future OpenDCRE release)
``current``     none (may be added in future OpenDCRE release)
``temperature`` none (may be added in future OpenDCRE release)
``none``        none
=============== ==============================================

Read
----

For the ``read`` action's field in the OpenDCRE emulator configuration, two fields may be configured, relating to the responses returned from a read command for the given device.

First, the ``repeatable`` field may be set to true or false, depending on whether it is desirable for the list of responses set in the responses field to repeat in a round-robin fashion, or if a device should stop returning data after its response list has been exhausted.

The ``responses`` field is a list of zero or more raw (integer) values that may be returned for a given read command.  The raw values are converted by the built-in OpenDCRE conversion functions, based on the given ``device_type``.  Some examples are given for the thermistor sensor device type in the ``simple.json`` file.

When a list of values is provided for responses, the emulator iterates sequentially through the items in that list, until the list is exhausted (if repeatable is set to "true", then the emulator returns to the beginning of the list).

An empty responses list means the device returns no data, which translates to a 500 error for the read command at the OpenDCRE REST API level (useful for simulating errors).  To always return the same single value, a responses list with a single element, and repeatable set to "true" will suffice.

Power
-----

For the ``power`` action's field in the OpenDCRE emulator configuration, similar fields are present - repeatable and responses.

For every power command (e.g. ``on``/``off``/``cycle``/``status``) issued to a power device in the OpenDCRE emulator, a response is returned from the responses list, which may be repeatable or non-repeatable.  The values in the responses list correspond to power status values returned over PMBUS from the hot swap controller on an OCP server, and are expressed as an integer value in the emulator configuration (see example above).  OpenDCRE converts the raw response to a friendly power status result using its built-in conversion functions.

Other Notes
-----------

The emulator configuration in ``simple.json`` is designed to provide a simple view and demonstration of how OpenDCRE works.  The OpenDCRE emulator is also used for testing purposes, and additional emulator configurations may be found under the ``/opendcre/opendcre_southbound/tests`` directory of the OpenDCRE Docker container.

An invalid emulator configuration will cause the OpenDCRE emulator to fail to start or function properly.

Hardware
--------

When using the OpenDCRE HAT board with OpenMistOS and OpenDCRE, no software or configuration changes are necessary.  The "scan" command (e.g.
::

    http://<ipaddress>:5000/opendcre/1.1/scan
    
) provides a real-time list of devices present on the HAT board.

To switch between the HAT and emulator, simply power-down the OpenMistOS Raspberry Pi, and add or remove the HAT.  On power-up, the HAT's presence or absence will be detected, determining whether or not the emulator should be used.
