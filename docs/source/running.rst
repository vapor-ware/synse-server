
.. _opendcre-running:

================
Running OpenDCRE
================

OpenDCRE is easy to start up - it just requires that the container be run. In the simplest case, OpenDCRE can be
started with
::

    docker run -p 5000:5000 vaporio/opendcre

But this wont do very much, since it will have no devices configured to issue commands to. To get OpenDCRE working with
real or even emulated hardware, there is a bit of configuration that needs to be done. Below, there is a "Quick Start"
approach to getting start with using OpenDCRE. After, the "Detailed Start" covers a bit more detail all the ways in
which OpenDCRE can be configured for running.

Quick Start
-----------

For the quick start, we will assume that we will be using an emulator, though the principles here should naturally
and clearly extend to real hardware as well. For simplicity, This will use a single emulator (for IPMI), but nothing
prevents you from configuring it with multiple emulators/devices as you see fit.

See the :ref:`opendcre-emulator` section for more complete documentation on how to configure and run the emulators.

For this example, lets say our IPMI emulator is running on 192.168.1.10, with username 'admin' and password 'admin'.

A configuration file should be created which specifies this emulator, which we will save locally as ``bmc_config.json``:

.. code-block:: json

    {
      "racks": {
        "rack_id": "rack_1",
        "bmcs": [
          {
            "bmc_ip": "192.168.1.10",
            "username": "admin",
            "password": "admin"
          }
        ]
      }
    }

Next, we just need to run OpenDCRE and mount in the IPMI configuration file to the appropriate location.
::

    docker run -p 5000:5000 -v `pwd`/bmc_config.json:/opendcre/bmc_config.json vaporio/opendcre:1.3

This will start OpenDCRE and reach out to 192.168.1.10 to register the IPMI Device and scan that BMC. To use your
own BMCs, you would simply provide the appropriate IP, username, and password for each BMC configured.

Volume Mount Locations
^^^^^^^^^^^^^^^^^^^^^^

Above, we say "mount the configuration to the appropriate location", but what are the appropriate locations?

==============  =============================
Devicebus Type  Container Configuration File
==============  =============================
plc             /opendcre/plc_config.json
ipmi            /opendcre/bmc_config.json
redfish         /opendcre/redfish_config.json
==============  =============================


Detailed Start
--------------

OpenDCRE devices are all set up by configuration. These configurations can either be built directly into the image
(if building a custom OpenDCRE image) or mounted into the container, which is the preferred approach as it is more
flexible.

When OpenDCRE starts, it reads in is configuration files to determine which devices are configured. By default,
OpenDCRE points to empty configurations for PLC, IPMI, and Redfish

.. code-block:: json

    {
      "devices": {
        "plc": {
          "from_config": "plc_config.json"
        },
        "ipmi": {
          "from_config": "bmc_config.json"
        },
        "redfish": {
          "from_config": "redfish_config.json"
        }
      }
    }

Where each of those files specifies a single rack with no devices on it, e.g. for IPMI

.. code-block:: json

    {
      "racks": [
        {
          "rack_id": "rack_1",
          "bmcs": []
        }
      ]
    }

So, when OpenDCRE starts up with no additional configurations provided, no devices will be registered with it, so
it really won't be able to perform any actions.

In the Quick Start example, we overwrite the existing "blank" IPMI BMC configuration file with one that has an actual
configuration in it (via the volume mount). With that, OpenDCRE will see that there is a device specified, and will attempt
to register it so that it can be used to issue commands to.

This same pattern applies to the other devicebus types, so if you want to configure OpenDCRE to work with a PLC device
and a Redfish device, you need only create the appropriate configuration files for them and volume-mount them to the
OpenDCRE container on startup.

It helps to familiarize yourself with the :ref:`opendcre-configuration` section as well as the configurations for the
:ref:`opendcre-plc-device`, :ref:`opendcre-ipmi-device`, and :ref:`opendcre-redfish-device` to know what configurations
are required.

Below is an example (dummy) OpenDCRE run command followed by an explanation of what each part does.
::

    docker run -d \
        -p 5000:5000 \
        -e VAPOR_DEBUG=true \
        -v `pwd`/plc_config.json:/opendcre/plc_config.json \
        -v `pwd`/ipmi_config.json:/opendcre/bmc_config.json \
        -v `pwd`/config_override.json:/opendcre/override/config.json \
        vaporio/opendcre \
        ./start_opendcre.sh

``-d``
    the ``-d`` flag is used to run OpenDCRE in "detached" mode - this means Docker will not attach to the console,
    so OpenDCRE will run in the background.

``-p 5000:5000``
    this maps the host's port 5000 to the OpenDCRE container's port 5000 - with this, you can use the OpenDCRE REST API
    on port 5000 of the host.

``-e VAPOR_DEBUG=true``
    this sets the ``VAPOR_DEBUG`` envirnment variable to ``true``, enabling debug logging. For more on this, see the
    :ref:`opendcre-debugging` section.

``-v `pwd`/plc_config.json:/opendcre/plc_config.json``
    this mounts in the "plc_config.json" file from the host to the "/opendcre/plc_config.json" location in the container.
    this will override the default (empty) PLC configurations.

``-v `pwd`/ipmi_config.json:/opendcre/bmc_config.json``
    this mounts in the "ipmi_config.json" file from the host to the "/opendcre/bmc_config.json" location in the container.
    this will override the default (empty) IPMI configurations.

``-v `pwd`/config_override.json:/opendcre/override/config.json``
    this mounts in the "config_override.json" file from the host to the "/opendcre/override/config.json" location in the
    container. this is used to override defaualt OpenDCRE configurations (including but not limited to device
    configurations). See the :ref:`opendcre-configuration` section for more on this.

``vaporio/opendcre``
    this is the image to run -- in this case the OpenDCRE image hosted on the Vapor IO DockerHub.

``./start_opendcre.sh``
    the command to run in the container. this particular command is superfluous as it is the default command that is
    run by OpenDCRE, but was included here for completeness of the example.
