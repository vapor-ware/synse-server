.. _deployment:

Deployment
==========
Running Synse Server locally is useful for testing and familiarizing yourself
with the API, but when using Synse Server, it will often be in some deployment.
This section goes through some simple examples of how to set up various deployments
with Synse Server and plugins.

Deploying with Docker Compose
-----------------------------
For a complete set of examples for deploying with ``docker compose``, see the
emulator example deployments in the `deploy/docker directory <https://github.com/vapor-ware/synse-server/tree/master/deploy/docker>`_
of the Synse Server source. This section goes into detail on how to deploy Synse Server
with an externally running emulator plugin configured for TCP communication.

For Synse Server, all that we really need to do is specify the plugin in the
container's configuration. As you may recall from the :ref:`configuration` section,
this can be done either by adding in our own YAML config file, or by specifying
an appropriate environment variable. Since we are only registering a single plugin
in this example, we'll keep things easier and just specify via environment variable.

We already know that we will run the plugin in TCP mode, so all that's left is naming
the plugin, and identifying which port it uses. The emulator plugin exposes port 5001
by default, so we'll use that. As for a name, since it is the emulator plugin, we can
just call it ``emulator``. Putting this all together, we get

.. code-block:: yaml

    environment:
      SYNSE_PLUGIN_TCP_EMULATOR: emulator-plugin:5001

Here, ``emulator-plugin`` is being used as the host name. We'll need to link in
the emulator container to the Synse Server container with that host name.

.. code-block:: yaml

    links:
      - emulator-plugin

This means that our emulator plugin service will be called ``emulator-plugin``. Before
we move on to that, we should fill out the rest of the Synse Server configuration, namely
specifying the container name, image, and ports

.. code-block:: yaml

    synse-server:
      container_name: synse-server
      image: vaporio/synse-server:latest-slim
      ports:
        - 5000:5000
      environment:
        SYNSE_PLUGIN_TCP_EMULATOR: emulator-plugin:5001
      links:
        - emulator-plugin


Now, to configure the emulator plugin portion. The emulator plugin is available
as a pre-built image ``vaporio/emulator-plugin``, so that will be the image we use here.
Since Synse Server is configured to reach the emulator on port 5001, we will want to
expose that port.

The only remaining bit is configuring the plugin. Plugin configuration is discussed in
the `SDK Documentation <https://github.com/vapor-ware/synse-sdk>`_. Briefly, a plugin takes
three types of configuration:

1. *prototype configuration* - This should be provided in the plugin image. Prototype
   configurations define the basic metadata of the devices that a plugin supports.
2. *instance configuration* - This is specified by the user. It specifies the instances
   of the prototypes that this particular plugin will be interfacing with.
3. *plugin configuration* - This is the general configuration for how the plugin should
   behave. For example, you can configure the plugin to perform device actions in parallel
   or in serial via this config.

The prototype configuration is provided in the the ``vaporio/emulator-plugin`` image, so
we do not have to configure that here. We do need to provide the instance config and the
plugin config. See the SDK Documentation for more information on these configs.

For our plugin config, we have the following ``config.yml``,

.. code-block:: yaml

    version: 1.0
    name: emulator
    debug: true
    network:
      type: tcp
      address: ":5001"

Instance configurations can be much larger, as there may be many devices. For simplicity
here, we will define a handful of temperature device instances in a file named ``devices.yml``.
For a more complete example, see the emulator example deployments in the ``deploy`` directory
of the Synse Server source repo.

.. code-block:: yaml

    version: 1.0
    locations:
      r1b1:
        rack: rack-1
        board: board-1
    devices:
      - type: temperature
        model: emul8-temp
        instances:
          - id: "1"
            location: r1b1
            info: Temperature Sensor 1
          - id: "2"
            location: r1b1
            info: Temperature Sensor 2
          - id: "3"
            location: r1b1
            info: Temperature Sensor 3
          - id: "4"
            location: r1b1
            info: Temperature Sensor 4

Briefly, this defines four 'emul8-temp' temperature sensors (which is backed by a prototype
that the plugin supports) on 'rack-1', 'board-1'. The rack and board designation here are
arbitrary for this example but are typically used to organized device across racks and boards.

With these two files saved in the current working directory, we can mount them into the
plugin emulator container.

.. code-block:: yaml

    volumes:
      - ./config.yml:/tmp/config/config.yml
      - ./devices.yml:/tmp/devices/devices.yml

While there are default search paths that these files can be placed on, here we put them
on custom paths. To specify to the plugin where these files are when not on a default
search path, we can tell it with environment variables

.. code-block:: yaml

    environment:
      # sets the override directory location for plugin configuration
      PLUGIN_CONFIG: /tmp/config
      # sets the override directory location for device instance configuration
      PLUGIN_DEVICE_PATH: /tmp/devices

Putting everything here together, we get the final compose file, ``compose.yml``:

.. code-block:: yaml

    version: "3"
    services:
      synse-server:
        container_name: synse-server
        image: vaporio/synse-server:latest-slim
        ports:
          - 5000:5000
        environment:
          SYNSE_PLUGIN_TCP_EMULATOR: emulator-plugin:5001
        links:
          - emulator-plugin

      emulator-plugin:
        container_name: emulator-plugin
        image: vaporio/emulator-plugin
        ports:
          - 5001:5001
        volumes:
          - ./config.yml:/tmp/config/config.yml
          - ./devices.yml:/tmp/devices/device.yml
        environment:
          PLUGIN_CONFIG: /tmp/config
          PLUGIN_DEVICE_PATH: /tmp/devices

To run it,

.. code-block:: console

    $ docker-compose -f compose.yml up -d

Once it starts up, you should be able to hit the Synse Server ``scan`` endpoint and
see the four temperature devices that were configured.

.. code-block:: console

    $ curl localhost:5000/synse/v2/scan
    {
      "racks":[
        {
          "id":"rack-1",
          "boards":[
            {
              "id":"board-1",
              "devices":[
                {
                  "id":"eb100067acb0c054cf877759db376b03",
                  "info":"Temperature Sensor 1",
                  "type":"temperature"
                },
                {
                  "id":"83cc1efe7e596e4ab6769e0c6e3edf88",
                  "info":"Temperature Sensor 2",
                  "type":"temperature"
                },
                {
                  "id":"db1e5deb43d9d0af6d80885e74362913",
                  "info":"Temperature Sensor 3",
                  "type":"temperature"
                },
                {
                  "id":"329a91c6781ce92370a3c38ba9bf35b2",
                  "info":"Temperature Sensor 4",
                  "type":"temperature"
                }
              ]
            }
          ]
        }
      ]
    }

Additionally, you can hit the ``plugins`` endpoint and should see the emulator plugin
specified there just as it was configured.

.. code-block:: console

    $ curl localhost:5000/synse/v2/plugins
    [
      {
        "name":"emulator",
        "network":"tcp",
        "address":"emulator-plugin:5001"
      }
    ]

To bring the deployment down,

.. code-block:: console

    $ docker-compose -f compose.yml down


Deploying with Kubernetes
-------------------------
A simple example deployment of Synse Server and the containerized Plugin Emulator can
be found in the project source's `deploy/k8s directory <https://github.com/vapor-ware/synse-server/tree/master/deploy/k8s>`_.
