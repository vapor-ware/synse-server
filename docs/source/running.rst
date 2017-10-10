
.. _synse-server-running:

====================
Running Synse Server
====================

Synse Server is easy to start up - it just requires that the container be run. In the simplest case, it can be
started with
::

    docker run -p 5000:5000 vaporio/synse-server

But this won't do very much, since it will have no devices configured to issue commands to. To get Synse Server working
with real or even emulated hardware, there is a bit of configuration that needs to be done. Below, there is a
"Quick Start" approach to getting started with using Synse Server. After, the "Detailed Start" covers a bit more detail
all the ways in which Synse Server can be configured for running.

Quick Start
-----------

For the quick start, we will assume that we will be using an emulator, though the principles here should naturally
extend to real hardware as well. For simplicity, this will use a single emulator (for IPMI).

See the :ref:`synse-server-emulator` section for more complete documentation on how to configure and run the emulators.

For this example, lets say our IPMI emulator is running on 192.168.1.10, with username 'admin' and password 'admin'.

A configuration file should be created which specifies this emulator, which we will save locally as ``bmc_config.json``:

.. code-block:: json

    {
      "racks": [
        {
          "rack_id": "rack_1",
          "bmcs": [
            {
              "bmc_ip": "192.168.1.10",
              "username": "admin",
              "password": "admin"
            }
          ]
        }
      ]
    }


We will also need a configuration that will alert the Synse application that this device exists
and should be registered. This is done through the override configuration. For more on this, see the
section on :ref:`synse-server-configuration`. We will save this override file locally as ``override_config.json``.

.. code-block:: json

    {
      "devices": {
        "ipmi": {
          "from_config": "/synse/bmc_config.json"
        }
      }
    }



Finally, we just need to run Synse Server and mount in the configuration files to the appropriate location.
::

    docker run -d \
        -p 5000:5000 \
        -v `pwd`/bmc_config.json:/synse/bmc_config.json \
        -v `pwd`/override_config.json:/synse/override/override_config.json \
        -e VAPOR_DEBUG=true \
        vaporio/synse-server

This will start Synse Server and reach out to 192.168.1.10 to register the IPMI Device and scan that BMC.
To use your own BMCs, you would simply provide the appropriate IP, username, and password for each BMC
configured.

In the above, the ``-d`` flag is not required. It just runs the container in the background. Also, the ``-e``
flag is not required, but it does enable debug logging which can be useful for seeing Synse Server go through
its startup process.


Detailed Start
--------------

Synse Server devices are all set up by configuration. These configurations can either be built directly into the image
(if building a custom Synse Server image) or mounted into the container, which is the preferred approach as it is more
flexible.

When Synse Server starts, it reads in configuration files to determine which devices should exist. By default,
Synse Server is not configured with any devices, so it won't do much other than sit there.

.. code-block:: json

    {
      "devices": {}
    }

In the Quick Start example, we overwrite the existing "blank" IPMI configuration with one that has an actual
configuration in it (via the volume mounts). With that, Synse Server will see that there is a device specified, and will attempt
to register it so that it can be used to issue commands to.

This same pattern applies to the other devicebus types, so if you want to configure Synse Server to work with a PLC device
and a Redfish device, you need only create the appropriate configuration files for them and volume-mount them to the
Synse Server container on startup.

It helps to familiarize yourself with the :ref:`synse-server-configuration` section as well as the configurations for
each of the devicebus types, as specified in the :ref:`synse-server-dbi` section.

Below is the same docker run command followed by an explanation of what each part does.
::

    docker run -d \
        -p 5000:5000 \
        -v `pwd`/bmc_config.json:/synse/bmc_config.json \
        -v `pwd`/override_config.json:/synse/override/override_config.json \
        -e VAPOR_DEBUG=true \
        vaporio/synse-server

``-d``
    the ``-d`` flag is used to run Synse Server in "detached" mode - this means Docker will not attach to the console,
    so Synse Server will run in the background.

``-p 5000:5000``
    this maps the host's port 5000 to the Synse Server container's port 5000 - with this, you can use the Synse Server API
    on port 5000 of the host.

``-v `pwd`/bmc_config.json:/synse/bmc_config.json``
    this mounts in the "bmc_config.json" file from the host to the "/synse/bmc_config.json" location in the container.

``-v `pwd`/override_config.json:/synse/override/override_config.json \``
    this mounts in the "override_config.json" file from the host to the "/synse/override/override_config.json" location
    in the container. this is used to override default Synse Server configurations (including but not limited to device
    configurations). See the :ref:`synse-server-configuration` section for more on this.

``-e VAPOR_DEBUG=true``
    this sets the ``VAPOR_DEBUG`` environment variable to ``true``, enabling debug logging. For more on this, see the
    :ref:`synse-server-debugging` section.

``vaporio/synse-server``
    this is the image to run -- in this case the Synse Server image hosted on the Vapor IO DockerHub.
