.. _configuration:

Configuration
=============
Synse Server tries to be flexible and easy to configure. Synse Server does not
require any configurations to run successfully, hence it can be run right out of
the box. Many of the configuration options have sane default values. There are a
number of configuration options which are described below.

Synse Server can be configured a number of ways. It has three sources of configuration

1. Built-in defaults
2. User defined config YAMLs
3. Environment variables

In the list above, each configuration mode takes precedence over the option above it.

The default built-in configurations should be enough to get Synse Server minimally running,
but it will not be very exciting or useful, since it has no plugins configured by
default. Recall from the architecture section that plugins are what provide the underlying
functionality to Synse Server, as they are the components that manages devices.

When configuring Synse Server for your own use, you will at the very least need to configure
the plugins for the devices you wish to interface with. The gRPC interface between Synse Server
and the plugins supports communicating over unix socket and TCP. In general, TCP is preferred,
but there may be cases where using a unix socket could make more sense.

.. note::

    While there is a distinction here between "TCP plugins" and "Unix socket plugins", it is
    important to note that the distinction is at a plugin configuration level. That is to say,
    all plugins that use the SDK have the capability of either being configured for TCP or unix
    socket.

Plugin Communication Modes
--------------------------
Here, we describe in more detail the differences in how to configure a TCP plugin versus a
Unix socket plugin. While largely similar, there are a few differences.

TCP
~~~
If a plugin is configured for TCP in Synse Server, it should also be configured for TCP in the
plugin configuration. See the SDK documentation for more info on plugin configuration.

There are two ways of configuring a TCP plugin with Synse Server:

1. By config file
2. By environment variable

Config File
...........
To configure **by config file**, you will need to specify the name of the plugin and the
host/port of the plugin under the ``plugin.tcp`` field of the configuration. As an example,
for a plugin named "foobar" that is listening on 10.10.1.8:5001, the configuration would
look like

.. code-block:: yaml

    plugin:
      tcp:
        foobar: 10.10.1.8:5001

Environment Variable
....................
To configure **by environment variable**, you will need to specify an environment variable
with the ``SYNSE_`` prefix followed by the configuration path, followed by the plugin name. The
value of the environment variable should be the host/port of the plugin. As an example, for a
plugin named "foobar" that is listening on 10.10.1.8:5001, the environment variable would
look like:

.. code-block:: none

    SYNSE_PLUGIN_TCP_FOOBAR=10.10.1.8:5001


Unix Socket
~~~~~~~~~~~
If a plugin is configured for Unix sockets in Synse Server, it should also be configured for Unix
sockets in the plugin configuration. See the SDK documentation for more info on plugin
configuration.

There are three ways of configuring a Unix socket plugin with Synse Server:

1. By config file
2. By environment variable
3. By using the default socket path

Config File
...........
To configure **by config file**, you will need to specify the name of the plugin and the
directory where the socket exists. The socket is expected to have the same name as the plugin.
This is specified under the ``plugin.unix`` field of the configuration. As an example,
for a plugin named "foobar" whose socket, "foobar.sock", is in the directory "/tmp/run", the
configuration would look like

.. code-block:: yaml

    plugin:
      unix:
        foobar: /tmp/run

Environment Variable
....................
To configure **by environment variable**, you will need to specify an environment variable
with the ``SYNSE_`` prefix followed by the configuration path, followed by the plugin name. The
value of the environment variable should be the directory containing the socket for the plugin.
As an example, for a plugin named "foobar" whose socket, "foobar.sock", is in the directory
"/tmp/run", the environment variable would look like:

.. code-block:: none

    SYNSE_PLUGIN_UNIX_FOOBAR=/tmp/run

Default Path
............
To configure **by using the default socket path**, then all you will have to do is put the socket
file into the default socket path for Synse Server (Note: if running Synse Server in a container,
this means volume mounting). The default path is ``/tmp/synse/procs``, so if you had a plugin named
"foobar" whose socket, "foobar.sock" was in "/tmp/synse/procs", then you would not need to specify
anything in the YAML configuration or via environment variable.

While its not necessary to specify anything in this case, it is often still good practice to
list it in the configuration. If there is a plugin whose socket exists in the default location
and you want to include it in the config for visibility, you can do so and omit the socket path -
this tell Synse Server to look for it in the default location.

.. code-block:: yaml

    plugin:
      unix:
        foobar:


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
        TCP-based plugin configurations. This should be a mapping where the
        key is the name of the plugin, and the value is the TCP host/port for
        that plugin, e.g. ``plugin1: 192.1.53.2:5022``

    :unix:
        Unix socket-based plugin configurations. This should be a mapping
        where the key is the name of the plugin socket, and the value is the
        directory it exists in, e.g. ``plugin1: /tmp/run``. The value can be
        left blank,e.g. ``plugin1:`` to signify that the socket is in the default
        location.

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
        emulator: localhost:6000
        plugin1: 54.53.52.51:5555
      unix:
        # a unix socket named 'plugin2' found in the default location
        plugin2:
        # a unix socket named 'plugin3' found in /tmp/run
        plugin3: /tmp/run
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
        emulator: localhost:5001

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
As mentioned earlier, all of the configuration options, except for the ``plugin``
configuration, can be set by environment variable as well. This is done by joining
the configuration key path with an underscore, upper casing, and appending to the
``SYNSE_`` prefix. That is to say, for a config ``{'foo': {'bar': 20}}``, to set
the value of *bar* to 30, you would set ``SYNSE_FOO_BAR=30``.

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
`Plugin Communication Modes`_ section for more on how to specify TCP and Unix
socket plugin configuration via the environment.
