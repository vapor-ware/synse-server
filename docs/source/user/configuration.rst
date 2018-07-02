.. _configuration:

Configuration
=============
Synse Server tries to be flexible and easy to configure. Its default configurations
allow it to run right out of the box. There are a number of configuration option
which are described below.

Synse Server has three sources of configuration:

1. Built-in defaults
2. User defined config (via YAML file)
3. Environment variables

In the list above, each configuration mode takes precedence over the option above it.

The default built-in configurations should be enough to get Synse Server minimally running,
but it will not be very exciting or useful, since it has no plugins configured by
default. Recall from the architecture section that plugins are what provide the underlying
functionality to Synse Server, as they are the components that manages devices.

When configuring Synse Server for your own use, you will at the very least need to configure
the plugins for the devices you wish to interface with. The gRPC interface between Synse Server
can be configured to use one of two supported protocols: TCP or Unix socket. In general, TCP is
preferred, but there may be cases where using a unix socket could make more sense.

.. note::

    While there is a distinction in the does between "TCP plugins" and "Unix socket plugins", it is
    important to note that the distinction is at a plugin configuration level. That is to say,
    all plugins that use the SDK have the capability of either being configured for TCP or unix
    socket -- they are not tied to a single protocol.

Plugin Registration
-------------------
Both TCP and Unix socket-based plugins can be configured either from config file or from
environment variable.

Config File
...........
All plugins are configured under the ``plugin`` section of the configuration file. There are
subsections for ``tcp`` and ``unix`` which take lists. The values in these lists would be the
address for the plugin. For TCP-based plugins, this could be the IP address (with optional
port). For Unix socket-based plugins, this would be the path to the socket.

.. code-block:: yaml

    plugin:
      tcp:
        - 10.10.1.2:5001
        - 10.10.1.4:5002
      unix:
        - /tmp/plugin/example.sock

Environment Variable
....................
Plugins can be configured from environment variable as well. TCP-based plugins would use
the ``SYNSE_PLUGIN_TCP`` environment variable, and Unix socket-based plugins would use
the ``SYNSE_PLUGIN_UNIX`` environment variable. The value should be a comma-separated list
of addresses. The equivalent environment-based configuration to the example config in the
Config File section, above, would be:

.. code-block:: none

    SYNSE_PLUGIN_TCP=10.10.1.2:5001,10.10.1.4:5002
    SYNSE_PLUGIN_UNIX=/tmp/plugin/example.sock


Default Path
............
Unix sockets have one more avenue of configuration. To make it a bit easier to deal with
unix sockets, a default path exists where they can be placed/mounted, and Synse Server
will find them automatically with no additional configuration. This default path is
``/tmp/synse/procs``. On startup, Synse Server will look through this directory and will
search for sockets. If it finds any, it will use them and attempt to establish communication
with a plugin.

If a plugin is configured this way, it will still show up in the unified config provided by
Synse Server's ``/config`` endpoint.


Kubernetes Service Discovery
............................
Plugins can also be registered via service discovery using Kubernetes Service Endpoints.
Examples of how this is done can be found in the :ref:`psdKubernetes` section. Currently,
Synse Server only supports service discovery by matching labels on a service endpoint.
In the future, discovery could be done using other bits of metadata and other Kubernetes
objects. The :ref:`configurationOptions` section below describes the config options for
service discovery via Kubernetes Service Endpoints.


.. _configurationOptions:

Configuration Options
---------------------
This section outlines all of the configuration options for Synse Server. Note that these
options are for the configuration YAML. These same options, excluding the plugin options
(see sections above), can be set via environment variable by using the ``SYNSE_`` prefix
on the upper-cased option name. For example, to set logging level to error via environment
variable, ``SYNSE_LOGGING=error``.


:logging:
    The logging level for Synse Server to use.

    | *default*: ``info``
    | *supported*: ``debug``, ``info``, ``warning``, ``error``, ``critical``

:pretty_json:
    Output the API response JSON so it is pretty and human readable.
    This adds spacing and newlines to the JSON output.

    | *default*: ``false``
    | *supported*: ``true``, ``false``

:locale:
    The locale to use for logging and error output.

    | *default*: ``en_US``
    | *supported*: ``en_US``

:plugin:
    Configuration options for registering plugins with Synse Server.

    :tcp:
        TCP-based plugin configuration. This should be a list of addresses
        for each of the TCP plugins to register, e.g. ``192.1.53.2:5022``

    :unix:
        Unix socket-based plugin configuration. This should be a list of
        addresses for each of the Unix socket plugins to register. A unix
        socket address is the path to the socket file, e.g. ``/tmp/example.sock``

    :discover:
        Configuration options for plugin service discovery.

        :kubernetes:
            Configuration options for plugin service discovery via Kubernetes.

            :endpoints:
                Configurations for plugin service discovery via Kubernetes
                service endpoints.

                :labels:
                    The endpoint labels to filter by to select the services
                    that are plugins. This should be a map where the key is
                    the label name and the value is the value that the label
                    should match to.

:cache:
    Configuration options for the Synse Server caches.

    :meta:
        Configuration options for the meta info caches. These caches
        store the device meta information returned by the configured plugins.

        :ttl:
            Time to live for the meta info caches, in seconds.

            | *default*: ``20``

    :transaction:
        Configuration options for the transaction cache. This cache tracks
        the active transactions for recent write events.

        :ttl:
            Time to live for the transaction cache, in seconds.

            | *default*: ``300``

:grpc:
    Configuration options relating to the gRPC communication layer
    between Synse Server and any configured plugins.

    :timeout:
        The timeout for the gRPC connection, in seconds.

        | *default*: ``3``


Examples
--------

Default Configuration
~~~~~~~~~~~~~~~~~~~~~
Below is what the default configuration for Synse Server looks like as YAML.

.. code-block:: yaml

    locale: en_US
    pretty_json: false
    logging: info
    cache:
      meta:
        ttl: 20
      transaction:
        ttl: 300
    grpc:
      timeout: 3

Complete Configuration
~~~~~~~~~~~~~~~~~~~~~~
Below is a valid (if contrived) and complete example configuration file.

.. code-block:: yaml

    logging: debug
    pretty_json: true
    locale: en_US
    plugin:
      tcp:
        - localhost:6000
        - 54.53.52.51:5555
      unix:
        - /tmp/run/example.sock
      discover:
        kubernetes:
          endpoints:
            labels:
              app: synse
              component: plugin
    cache:
      meta:
        # time to live in seconds
        ttl: 20
      transaction:
        # time to live in seconds
        ttl: 300
    grpc:
      # timeout in seconds
      timeout: 5


Configuring Synse Server
------------------------
By now, you should have a good understanding of the configuration options for
Synse Server as well as the different ways it can take configuration. Now, lets
look at how to actually pass custom configurations to Synse Server.

Specifying a Custom Config File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Synse Server looks for a YAML file (``.yml`` or ``.yaml`` extension) named ``config``
in the current working directory, ``./``, and within the ``synse/config`` directory.
If the configuration file (``config.{yaml|yml}``) is not found in either of those
locations, no config file is used and the Synse Server configuration will be built
off of the defaults and whatever values are specified in the environment.

When running Synse Server as a Docker image, you would either have to:

- volume mount the custom configuration
- build a custom Synse Server image that includes your configuration

The first option is obviously the most flexible, thus preferable.

To mount a custom configuration file, you must first have a configuration file.
For this example, consider the YAML below to be contained within ``custom-config.yml``.

.. code-block:: yaml

    logging: debug
    pretty_json: true
    plugin:
      tcp:
        - localhost:5001

We can mount this into the Synse Server container with ``docker run``, e.g.

.. code-block:: bash

    docker run -d \
        -p 5000:5000 \
        -v $PWD/custom_config.yml:/synse/config/config.yml \
        --name synse-server \
        vaporio/synse-server

Assuming the configuration is correct and Synse Server comes up, you should be able
to verify that the config was picked up either by looking at the Synse Server logs,
or by hitting the ``/config`` endpoint

.. code-block:: bash

    curl localhost:5000/synse/2.0/config

Configurations can also be mounted in via ``docker-compose``

.. code-block:: yaml

    version: "3"
    services:
      synse-server:
        container_name: synse-server
        image: vaporio/synse-server
        ports:
          - 5000:5000
        volumes:
          - ./custom_config.yml:/synse/config/config.yml


Specifying Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
As mentioned earlier, configuration options can be set by environment variable as well.
This is done by joining the configuration key path with an underscore, upper casing, and
appending to the ``SYNSE_`` prefix. That is to say, for a config ``{'foo': {'bar': 20}}``,
to set the value of *bar* to 30, you would set ``SYNSE_FOO_BAR=30``.

A more real example is to set the logging level to debug and to change the transaction
cache TTL.

.. code-block:: bash

    docker run -d \
        -p 5000:5000 \
        -e SYNSE_LOGGING=debug \
        -e SYNSE_CACHE_TRANSACTION_TTL=500 \
        --name synse-server \
        vaporio/synse-server

This can also be done via ``docker-compose``

.. code-block:: yaml

    version: "3"
    services:
      synse-server:
        container_name: synse-server
        image: vaporio/synse-server
        ports:
          - 5000:5000
        environment:
          - SYNSE_LOGGING=debug
          - SYNSE_CACHE_TRANSACTION_TTL=500

A combination of both config file and environment configs can be provided, but
as mentioned earlier, environment variable based configuration takes precedence
over file based configuration.

Specify Plugins via Environment
...............................
Plugin configurations can be specified via environment variable, but how this
is done differs slightly from the other configuration options. See the
`Plugin Registration`_ section for more on how to specify TCP and Unix
socket plugin configuration via the environment.
