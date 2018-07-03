.. _quickstart:

Quickstart
==========
This section assumes that you have gone through the steps of :ref:`getting` and
now have a Synse Server image, either pulled from DockerHub or built locally.

Out of the box
--------------
Out of the box, Synse Server should work with no configuration necessary. That said,
it will not do anything exciting without a plugin to provide device information. All
non-``slim`` images come with a built-in emulator plugin, which is also available as a
standalone image (`vaporio/synse-emulator-plugin <https://github.com/vapor-ware/synse-emulator-plugin>`_).
The data it provides is random, but it does allow you to immediately pick up Synse Server
and play around with the API without having to configure any hardware or additional plugins.


Running Synse Server
--------------------
Synse Server was designed to run within a Docker container. Running Synse Server is
as easy as

.. code-block:: console

    $ docker run -p 5000:5000 vaporio/synse-server

The above command will start Synse Server running minimally with no emulator or
anything. It can still be useful to see how it behaves with nothing configured, but
it would be more interesting to have Synse Server provide data.

.. code-block:: console

    $ docker run -d \
        -p 5000:5000 \
        --name synse \
        vaporio/synse-server enable-emulator

This will start Synse Server and enable the built-in emulator plugin. In either case,
once the container is up, you can verify that it is reachable with

.. code-block:: console

    $ curl http://localhost:5000/synse/test
    {
      "status": "ok",
      "timestamp": "2018-02-26 16:58:07.844486"
    }

If this fails, check the container is running (``docker ps -a``). You may also check
the container logs (``docker logs synse``) to see if any errors are reported.

You can get the API version of Synse Server, which is used in subsequent API calls.

.. code-block:: console

    $ curl http://localhost:5000/synse/version
    {
      "version": "2.1.0",
      "api_version": "v2"
    }

Finally, you can see what devices are available to Synse Server by running a scan, using
the API version you got above.

.. code-block:: console

    $ curl http://localhost:5000/synse/v2/scan

This lists all devices that are configured with the registered plugins (in this case,
the emulator) and can be managed and monitored by Synse Server. To see what else Synse
Server is capable of, see the `API Reference Documentation <https://vapor-ware.github.io/synse-server/>`_.


Emulator Plugin
---------------
The :ref:`configuration` section goes into some detail about the types of plugins
and how they are configured. The emulator plugin is a regular plugin that is just
included with Synse Server and run within the same container. While this approach
is not generally recommended for plugin deployment, it is done here to make the
initial setup, exploration, and development of Synse Server easier.

The emulator plugin can be run external to Synse Server, which is useful when
learning how to set up a :ref:`deployment` with Synse Server and plugins.