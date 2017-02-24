
.. _opendcre-emulator:

=========
Emulators
=========

OpenDCRE comes with pre-built emulators for each supported devicebus type so that it can emulate API commands and
functionality in the absence of supported hardware. This is especially useful for testing and experimenting with
OpenDCRE.

PLC Emulator
------------
The PLC Emulator runs as a background process in the OpenDCRE container itself. It uses socat to create a connected
pair of virtual TTY devices that can be used to simulate serial communications without hardware. The main difference
between the emulated PLC comms and hardware PLC comms is that the emulator does not require the additional steps
of configuring the serial device and initializing the SIG60 PLC modem.

The emulator itself is a primitive Python process that is provided a configuration file on startup to map board/device
ids to raw packet readings. These packet readings are returned to the device on the other end of the virtual serial
connection. Faults, repeated values, cycling values, or no value returns are supported by the PLC emulator through its
config file. State can also be preserved in cases where an incoming command mutates state (e.g. turns on an LED) - state
honoring may be enabled/disabled in the emulator configuration for a board/device.

Configuration Example
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

    {
      "boards": [
        {
          "board_id": "00000001",
          "firmware_version": "OpenDCRE Emulator v1.0.0 - Standalone Server",
          "devices": [
            {
              "host_info": {
                "repeatable": true,
                "responses": [
                  "i10.10.1.16,htest-server0"
                ]
              },
              "has_state": true,
              "boot_target": "B0",
              "pxe" : "B1",
              "no_override": "B2",
              "hdd": "B0",
              "asset_info": {
                "repeatable": true,
                "responses": [
                  "Quanta,0001,Winterfell,S1234567,rack mount chassis,P1234567,S1234567,A1234567,Quanta,P1234567,Winterfell,S1234567,v1.2.0"
                ]
              },
              "device_type": "system",
              "device_id": "0001"
            },
            {
              "read": {
                "repeatable": true,
                "responses": [
                  4100, 4100, 4000, 4000, 3900, 3900, 3800, 3800, 3700, 3700,
                  3800, 3800, 3900, 3900, 4000, 4000, 4100, 4100, 4200, 4200
                ]
              },
              "write": {
                "repeatable": true,
                "responses": [
                  "W1"
                ]
              },
              "device_type": "fan_speed",
              "device_id": "0002"
            },
            {
              "read": {
                "repeatable": true,
                "responses": [
                  4100, 4100, 4000, 4000, 3900, 3900, 3800, 3800, 3700, 3700,
                  3800, 3800, 3900, 3900, 4000, 4000, 4100, 4100, 4200, 4200
                ]
              },
              "write": {
                "repeatable": true,
                "responses": [
                  "W1"
                ]
              },
              "device_type": "fan_speed",
              "device_id": "0003"
            },
            {
              "device_id": "0004",
              "device_type": "power",
              "has_state": true,
              "on": [
                "0,10000,0,0", "0,11000,0,0", "0,12000,0,0", "0,13000,0,0",
                "0,14000,0,0", "0,15000,0,0", "0,14000,0,0", "0,13000,0,0",
                "0,12000,0,0", "0,11000,0,0"
              ],
              "off": "64,0,0,0",
              "power": [
                "0,10000,0,0", "0,11000,0,0", "0,12000,0,0", "0,13000,0,0",
                "0,14000,0,0", "0,15000,0,0", "0,14000,0,0", "0,13000,0,0",
                "0,12000,0,0", "0,11000,0,0"
              ]
            },
            {
              "device_id": "0005",
              "device_type": "led",
              "has_state": true,
              "read": 0,
              "write": 0,
              "on": 1,
              "off": 0
            },
            {
              "read": {
                "repeatable": true,
                "responses": [
                  28.78, 29.77, 30.75, 31.84, 32.82, 33.81, 34.89, 35.88, 36.96, 37.94,
                  38.93, 40.21, 41.27, 42.33, 43.39, 44.45, 45.61, 46.57, 47.63, 48.69,
                  49.75, 48.69, 47.63, 46.57, 45.61, 44.45, 43,39, 42.33, 41.27, 40.21,
                  38.93, 37.94, 36.96, 35.88, 34.89, 33.81, 32.82, 31.84, 30.75, 29.77
                ]
              },
              "device_type": "temperature",
              "device_id": "2000"
            },
            {
              "read": {
                "repeatable": true,
                "responses": [
                  28.78, 29.77, 30.75, 31.84, 32.82, 33.81, 34.89, 35.88, 36.96, 37.94,
                  38.93, 40.21, 41.27, 42.33, 43.39, 44.45, 45.61, 46.57, 47.63, 48.69,
                  49.75, 48.69, 47.63, 46.57, 45.61, 44.45, 43,39, 42.33, 41.27, 40.21,
                  38.93, 37.94, 36.96, 35.88, 34.89, 33.81, 32.82, 31.84, 30.75, 29.77
                ]
              },
              "device_type": "temperature",
              "device_id": "4000"
            }
          ]
        }
      ]
    }

Configuration Fields
^^^^^^^^^^^^^^^^^^^^

:boards:
    A list of boards configured for the emulator, where a single board configuration would represent a single
    hardware board that should exist.

:board_id:
    The internal id for a single board. Board Ids in OpenDCRE have a 4 byte width and should be expressed in the
    config as a 4-byte hex string. Board Ids should be unique across all device instances. For PLC, the board id
    range starts at 0x00000000.

:firmware_version:
    The version string for the board, which would be returned by the OpenDCRE “version” command.

:devices:
    A list of all device configurations which are associated with that given board.

:repeatable:
    A flag which denotes that the given responses should repeat. This means that when the emulator has cycled through
    all of the responses in the responses list, it will return to the beginning of the list. If this is set to ``false``,
    upon reaching the end of the responses list, the emulator will not return data, causing an error to be raised in
    OpenDCRE (as the emulator will not respond).

:responses:
    A list of canned responses for the emulator to return.

:host_info:
    The response(s) to return on a system "host info" command.

:asset_info:
    The response(s) to return on a system "asset info" command.

:read:
    The response(s) to return on a "read" command.

:write:
    The response(s) to return on a "write" command.

:on:
    The response(s) to return on a "power on" command.

:off:
    The response(s) to return on a "power off" command.

:power:
    The response(s) to return on a "power status" command.

:has_state:
    If true, then state information is preserved relative to the command (e.g. "on" or "off" for power), in which
    case subsequent reads retrieve a response relative to the persisted state. When state is undefined, the default
    response (e.g. "power") for the command is returned. When ``has_state`` is false, the response relative to an
    incoming command is returned (e.g. the response for "on" for a power "on" command).

:boot_target:
    Indicates the response sent back for a "get" of boot target (B0 == no_override, B1 == pxe, B2 == hdd).

:pxe:
    The response sent when boot target of PXE is set.

:no_override:
    The response sent when boot target of no_override is set.

:hdd:
    The response sent when boot target of HDD is set.

:device_type:
    Indicates the type of device that a device entry represents. This is also the ``device_type`` reported back in
    OpenDCRE REST API scan results. Valid device types include:

    - ``thermistor``
    - ``power``
    - ``humidity``
    - ``pressure``
    - ``led``
    - ``system``
    - ``fan_speed``
    - ``temperature``

    .. versionchanged:: 1.2
        In previous releases, a device type of ``none`` indicated that no device is present at a given ``device_id`` on the
        given board, and may be ignored.  In OpenDCRE v1.2 the ``none`` device type has been removed.

:device_id:
    The internal device id of the device being configured, expressed as a 2-byte numeric value as a hex string. In
    most cases, a device id of "0001" is sufficient.


Additional Information on Configuration Fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Device Type
"""""""""""
A field corresponding to the action supported for a given device type is required. A map of device types to
supported actions is below:

=============== ==============================================
Device Type     Action Supported
--------------- ----------------------------------------------
``thermistor``  ``read``
``temperature`` ``read``
``power``       ``power``
``humidity``    ``read``
``pressure``    ``read``
``led``         ``read``, ``write``
``fan_speed``   ``read``, ``write``
``system``      ``asset info``, ``boot target``
=============== ==============================================

Read
""""
For the ``read`` action's field in the OpenDCRE emulator configuration, two fields may be configured relating to the
responses returned from a read command for the given device.

First, the ``repeatable`` field may be set to true or false, depending on whether it is desirable for the list of
responses set in the responses field to repeat in a round-robin fashion, or if a device should stop returning data
after its response list has been exhausted.

The ``responses`` field is a list of zero or more values that may be returned for a given read command.  The raw
values are converted (where necessary) by the built-in OpenDCRE conversion functions, based on the given ``device_type``.

When a list of values is provided for responses, the emulator iterates sequentially through the items in that list,
until the list is exhausted (if repeatable is set to "true", then the emulator returns to the beginning of the list).

An empty responses list means the device returns no data, which translates to a 500 error for the read command at the
OpenDCRE REST API level (useful for simulating errors).  To always return the same single value, a responses list with
a single element, and repeatable set to "true" will suffice.

Read Response Format
""""""""""""""""""""

The table below describes the response format for each device type for ``read`` commands to the emulator.

=============== ==============================================
Device Type     Format
--------------- ----------------------------------------------
``thermistor``  integer, converted by OpenDCRE
``temperature`` numeric, sent back as numeric value (e.g. 28.78)
``humidity``    numeric, converted by OpenDCRE
``led``         integer, ``1`` is ``on`` and ``0`` is ``off``; all other values are errors
``fan_speed``   integer, sent back as integer value (e.g. 4100)
=============== ==============================================

Values that do not conform to the above formats will result in errors to ``read`` requests made to the emulator, as
they would on the device bus.

Write
"""""

For the ``write`` action's field in the OpenDCRE emulator configuration, two fields may be configured, relating to the
responses returned from a write command for the given device.  The fields are laid out and function in the same manner
as ``read`` fields.

Write Response Format
"""""""""""""""""""""

The table below describes the response format for each device type for ``write`` commands to the emulator.

=============== ==============================================
Device Type     Format
--------------- ----------------------------------------------
``led``         string - ``W1`` is successful, while ``W0`` is unsuccessful; all other values are errors.
``fan_speed``   string - ``W1`` is successful, while ``W0`` is unsuccessful; all other values are errors.
=============== ==============================================

Values that do not conform to the above formats will result in errors to ``write`` requests made to the emulator, as
they would on the device bus.

Writing to a device from OpenDCRE to the emulator does not currently result in any state change for a corresponding
device in the emulator. That functionality may be added in a future release.

Power
"""""

For the ``power`` action's field in the OpenDCRE emulator configuration, similar fields are present - repeatable and responses.

For every power command (e.g. ``on``/``off``/``cycle``/``status``) issued to a power device in the OpenDCRE emulator,
a response is returned from the responses list, which may be repeatable or non-repeatable.  The values in the responses
list correspond to power status values returned over PMBUS from the hot swap controller on an OCP server, and are
expressed as an integer value in the emulator configuration (see example above).  OpenDCRE converts the raw response
to a friendly power status result using its built-in conversion functions.

Other Notes
"""""""""""

The OpenDCRE emulator is also used for testing purposes, and additional emulator configurations may be found
under the ``/opendcre/opendcre_southbound/tests/data`` directory of the OpenDCRE Docker container.

An invalid emulator configuration will cause the OpenDCRE emulator to fail to start or function properly.

Additional features of the emulator that may be used by advanced users or hardware/protocol developers include:

- Ability to send back raw bytes for responses to ``scan``, ``version``, ``read``, ``write``, and ``power`` commands.
  In tests, this can be seen where a list (or list of lists) of integer values is specified for a given response.
  Special sentinel values (999, 10xx) are used to place sequence numbers and checksums into the packet stream.
- Ability to support command retries in cases of invalid packets, line noise, etc.
- Ability to support 'scan-all' command and retries using time-division multiplexing; success and failure scenarios
  may be implemented for various configurations.  See the ``test-scanall`` tests.


Running the Emulator
^^^^^^^^^^^^^^^^^^^^
To run the PLC emulator, simply specify the startup script for the PLC emulator.
::

    docker run -p 5000:5000 vaporio/opendcre ./start_opendcre_plc_emulator.sh

or, if using docker-compose:

.. code-block:: yaml

    opendcre:
      image: vaporio/opendcre
      command: ./start_opendcre_plc_emulator.sh
      ports:
        - 5000:5000

The examples above will start the emulator with the default configuration file, found at
``/opendcre/opendcre_southbound/emulator/plc/data/example.json``. To specify different emulator configurations, simply
pass that file as an argument to the emulator start script. Note that if the non-default emulator configuration is not
built into the OpenDCRE image, it will need to be volume-mounted in, e.g.
::

    docker run \
        -p 5000:5000 \
        -v `pwd`/emulator_config:/opendcre/new_emulator_config.json \
        vaporio/opendcre \
        ./start_opendcre_plc_emulator.sh /opendcre/new_emulator_config.json



IPMI Emulator
-------------

For IPMI communications, there is an IPMI emulator which exists as a Dockerized Python multithreaded UDP server that
accepts inbound UDP IPMI packets, processes them, and returns a response based on the emulator configuration and
internal state.

The IPMI Emulator, which is perhaps better described as a BMC Emulator, is stateful where applicable. For example, one
can set the boot target or LED state on the emulator and a subsequent examination of either should reveal the state to
be the new values it was set to.

The IPMI Emulator is primarily designed to work with pyghmi, as that is the library used within OpenDCRE to issue IPMI
commands. To accommodate pyghmi, the emulator supports:
- HMAC-SHA1-96 integrity checking
- RAKP_HMAC_SHA1 authentication
- AES_CBC_128 encryption.
The encrypted mode can be tested using pyghmi or ipmitool.

For ease of use and simplicity for debugging, it also supports no authentication/encryption which allows all bytes
to be examined (e.g. with Wireshark). This unencrypted mode can be tested using ipmitool.

The IPMI emulator is largely just a framing device which unpacks incoming requests and packs outgoing responses. The
actual logic to handle commands is often simple, typically just returning values either from internal state or
emulator configuration.

Configuration Example
^^^^^^^^^^^^^^^^^^^^^

The IPMI Emulator configuration lives in the ``opendcre/opendcre_southbound/emulator/ipmi/data`` directory and is built
into the emulator’s Docker image (at the same path, starting at root). Configurations can be changed by either
- Modifying the source configurations and rebuilding the Docker image
- Mounting in configuration overrides with Docker volumes.

There are four configuration files associated with the IPMI emulator

.. note::
    All of the raw bytes specified in these config files were taken off the wire (using Wireshark) when communicating
    with a real BMC.

bmc.json
""""""""
*bmc.json* contains the configurations for the mock BMC that is the IPMI emulator. It allows the specification of
device info, chassis info, channel authentication capabilities, and dcmi configurations. Generally, the configurations
specified in this file are the raw bytes that make up the IPMI responses.

.. code-block:: json

   {
     "device": {
       "device_id": "20",
       "device_revision": "01",
       "device_availability": "03",
       "minor_firmware_revision": "16",
       "ipmi_version": "02",
       "additional_device_support": "bf",
       "manufacturer_id": 47488,
       "product_id": 2566
     },
     "chassis": {
       "current_power_state": "01",
       "last_power_event": "00",
       "misc_state": "40",
       "bootdev": "no_override"
     },
     "channel_auth_capabilities": {
       "channel": "01",
       "version_compatibility": "96",
       "user_capabilities": "06",
       "supported_connections": "03",
       "oem_id": 21317,
       "oem_auxiliary_data": "00"
     },
     "capabilities": {
       "hpm": ["81", "b4", "cb", "20", "08", "3e", "c1", "d9"],
       "picmg": ["81", "b4", "cb", "20", "10", "00", "c1", "0f"],
       "vita": ["81", "b4", "cb", "20", "14", "00", "c1", "0b"]
     },
     "dcmi": {
       "power": {
         "current_watts": [185, 188, 186, 189, 188, 192, 195, 199, 210, 211, 213, 211, 212],
         "min_watts": 150,
         "max_watts": 250,
         "avg_watts": 200,
         "reporting_interval_ms": 305000
       },
       "capabilities": {
         "1": ["dc", "01", "05", "02", "00", "01", "07"],
         "2": ["dc", "01", "05", "02", "00", "00", "00", "00", "00"],
         "3": ["dc", "01", "05", "02", "20", "00"],
         "4": ["dc", "01", "05", "02", "ff", "ff", "ff"],
         "5": ["dc", "01", "05", "02", "01", "00"]
       }
     }
   }

fru.json
""""""""
*fru.json* contains the raw configuration data for the mock BMC’s FRU. The config file specifies the FRU inventory
area and the raw data that makes up the FRU.

.. code-block:: json

    {
      "inventory_area": 1024,
      "device_access": 0,
      "data": [
        "01", "00", "00", "01", "06", "00", "00", "f8", "01", "05", "00",
        "00", "00", "00", "ca", "53", "75", "70", "65", "72", "6d", "69",
        "63", "72", "6f", "c0", "ca", "20", "20", "20", "20", "20", "20",
        "20", "20", "20", "20", "c0", "c0", "c1", "00", "00", "00", "00",
        "00", "00", "fc", "00", "01", "03", "00", "c0", "c0", "c0", "c0",
        "ca", "20", "20", "20", "20", "20", "20", "20", "20", "20", "20",
        "c0", "c0", "c1", "00", "00", "b1"
      ]
    }

sdr.json
""""""""
*sdr.json* contains the raw configuration data for the mock BMC’s SDR. This includes the version, record count,
free space, latest addition, latest erase, and operation support. The configuration for the actual SDR records is
not specified in this file, but in *sdr_entries.json*.

.. code-block:: json

    {
      "sdr_version": 1.5,
      "record_count": 21,
      "free_space": 1663,
      "latest_addition_ts": 0,
      "latest_erase_ts": 0,
      "operation_support": "2f"
    }

sdr_entries.json
""""""""""""""""
*sdr_entries.json* is the config file where all device records belonging to the SDR are defined. The number of
devices defined in this config should match the device count specified in *sdr.json*. For each record, an id,
sensor type, data, readings, event messages, and threshold comparison field should be specified. The sensor type
field is not used by the IPMI emulator, but is used as a convenient means of labeling the record with a human-readable
description.

.. code-block:: none

    {
      "records": [
        {
          "id": "0000",
          "sensor_type": "System Temp",
          "data": [
            "04", "00", "51", "01", "36", "20", "00", "11", "07", "01", "7d", "68",
            "01", "01", "80", "7a", "80", "7a", "3f", "3f", "80", "01", "00", "00",
            "01", "00", "00", "00", "00", "00", "07", "2d", "4a", "fc", "7f", "80",
            "4f", "4d", "4b", "f7", "f9", "fb", "02", "02", "00", "00", "00", "cb",
            "53", "79", "73", "74", "65", "6d", "20", "54", "65", "6d", "70"
          ],
          "readings": [
            49, 49, 48, 47, 48
          ],
          "event_messages": "c0",
          "threshold_comparison": ["c0"]
        },
        {
          "id": "0047",
          "sensor_type": "CPU Temp",
          "data": [
            "47", "00", "51", "01", "33", "20", "00", "12", "03", "01", "7f", "68",
            "01", "01", "80", "7a", "80", "7a", "3f", "3f", "80", "01", "00", "00",
            "01", "00", "00", "00", "00", "00", "07", "1e", "59", "fc", "7f", "80",
            "5f", "5a", "55", "f5", "f8", "fb", "02", "02", "00", "00", "00", "c8",
            "43", "50", "55", "20", "54", "65", "6d", "70"
          ],
          "readings": [
            41, 40, 41, 41
          ],
          "event_messages": "c0",
          "threshold_comparison": ["c0"]
        },
        {
          "id": "008a",
          "sensor_type": "CPU FAN",
          "data": [
            "8a", "00", "51", "01", "32", "20", "00", "41", "1d", "01", "7d", "68",
            "04", "01", "95", "7a", "95", "7a", "3f", "3f", "00", "12", "00", "00",
            "b9", "00", "00", "c0", "00", "01", "07", "80", "aa", "14", "ff", "00",
            "b2", "af", "ac", "10", "11", "12", "01", "01", "00", "00", "00", "c7",
            "43", "50", "55", "20", "46", "41", "4e"
          ],
          "readings": [
            34, 34, 35, 34, 33
          ],
          "event_messages": "c0",
          "threshold_comparison": ["c0"]
        },
        ...
        (abridged for brevity)
      ]
    }

Getting the Emulator
^^^^^^^^^^^^^^^^^^^^
Since the IPMI Emulator is a standalone image, it needs to either be pulled from DockerHub, or built from Dockerfile.

From DockerHub,
::

    docker pull vaporio/ipmi-emulator-x64

From Dockerfile, first navigate to ``opendcre_southbound/emulator/ipmi``. Then, you can build the IPMI emulator image
with
::

    make build-x64

Running / Using the Emulator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Running the emulator in isolation is straightforward enough. Once you have the image, you can run it either with docker:
::

    docker run --name ipmi-emulator -p 623:623/udp vaporio/ipmi-emulator-x64

or with docker-compose
::

    docker-compose -f ipmi-emulator.yml up --build -d ipmi-emulator

where ``ipmi-emulator.yml`` contains

.. code-block:: yaml

   ipmi-emulator:
     container_name: ipmi-emulator
     image: vaporio/ipmi-emulator-x64
     command: ./start_ipmi_emulator.sh
     ports:
       - 623:623/udp

While other emulators (e.g. the PLC emulator) are built in to OpenDCRE and can be run from the same container, the
IPMI emulator must be run from a separate container, as shown above.

This is done in part for emulator isolation, but also because it allows for more flexible test setups. For instance,
with the emulator running in a separate container it is possible to spin up multiple emulator instances, each with
their own configuration, to emulate OpenDCRE performance against different BMC models. Additionally, with
docker-compose, OpenDCRE can have multiple proxies to the same emulator to simulate a full rack, cluster,
or multi-cluster of BMCs.

.. warning::
    When using the IPMI emulator in a proxied fashion, where multiple composefile links point to the same emulator,
    the number of requests issued against the emulator can become an issue, especially under high network latency,
    where the requests back up and time out.

    When run locally, this had caused the emulator to freeze up and communications between OpenDCRE and the emulator
    fail. One solution to this is to run the IPMI Emulator on a separate instance/machine when there will be heavy
    load placed upon it. This will ensure that it is given enough machine resources to operate at full capacity -
    although network latency can then become an issue.

    Running the emulator on a separate instance/machine is recommended even without heavy load, for stability
    and performance.

Above, we describe how to run an IPMI emulator. Some additional configuration will need to happen with OpenDCRE in
order for it to register the IPMI emulator as a usable interface.

The networking between the emulator and OpenDCRE is determined by the BMC config used by OpenDCRE. For example,
if there were a BMC config containing the record:

.. code-block:: json

    {
      "bmc_ip": "localhost",
      "username": "ADMIN",
      "password": "ADMIN"
    }

we would want the emulator to be running on the same machine as OpenDCRE, as localhost should resolve to the emulator.

The containers can also be linked in the composefile, if running on the same machine, so we can reference the emulator
using the container name as a hostname:

.. code-block:: json

    {
      "bmc_ip": "ipmi-emulator",
      "username": "ADMIN",
      "password": "ADMIN"
    }

Of course, a plain IP for the machine running the emulator can be supplied as the bmc_ip without any need to create
container links.

An example (abridged) composefile with the two containers linked is as follows:

.. code-block:: yaml

    opendcre:
      image: vaporio/opendcre-core-x64
      command: ./start_opendcre.sh
      ports:
        - 5000:5000
      links:
        - ipmi-emulator

    ipmi-emulator:
      image: vaporio/ipmi-emulator-x64
      ports:
        - 623:623/udp

Note that here, the OpenDCRE instance was started without running any other emulator. While it is possible (and fine)
to run the IPMI emulator alongside any of the serial emulators, keeping things isolated to IPMI-only for testing is
usually prudent.


Redfish Emulator
----------------

.. warning::
    Redfish support is in beta as of OpenDCRE v1.3.0

Like the IPMI emulator, the Redfish Emulator is a standalone Dockerized python application. It runs a simple
Flask webserver that serves up statically defined configuration data. It supports the basic Redfish commands and is
stateful, for operations where state can be preserved (e.g. turning an LED on). By default, the Redfish emulator
runs on port 5040. This can be changed by updating the Dockerfile and specifying the correct port mapping at run time.

Configuration
^^^^^^^^^^^^^
The configuration files which make up the Redfish emulator backend are too numerous to include here - instead, see the
`Redfish mockups <http://redfish.dmtf.org/redfish/v1>`_ which the configuration hierarchy is based off of.

To re-configure the Redfish emulator, either a new emulator image can be built with the new configuration placed in the
emulator's `Resources` directory, or it can be volume mounted in over the emulator's `Resources` directory.


Getting the Emulator
^^^^^^^^^^^^^^^^^^^^
Since the Redfish Emulator is a standalone image, it needs to either be pulled from DockerHub, or built from Dockerfile.

From DockerHub,
::

    docker pull vaporio/redfish-emulator-x64

From Dockerfile, first navigate to ``opendcre_southbound/emulator/redfish``. Then, you can build the Redfish emulator
image with
::

    make build-x64

Running the Emulator
^^^^^^^^^^^^^^^^^^^^
Running the Redfish emulator is simple, given that the desired configurations (whether they be the default or custom
built-in/volume-mounted configurations) are correctly placed in the image:
::

    docker run -p 5040:5040 vaporio/redfish-emulator-x64

