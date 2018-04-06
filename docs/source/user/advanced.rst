.. _advancedUsage:

Advanced Usage
==============
This section covers some of the more advanced features, components, and usage
of Synse Server.

Health Check / Liveness Probe
-----------------------------

When creating a :ref:`deployment` with Docker Compose, Kubernetes, etc., you can set a
"health check" (or liveness and readiness probe) for the service. While you can define
your own, Synse Server comes with one build in at ``bin/ok.sh``. This will check that the
*/test* endpoint is reachable and returning a 200 status with 'ok' in the JSON status response.

To illustrate, below is a simple compose file to run a Synse Server instance (with no plugins
configured, for simplicity of the example)

.. code-block:: yaml

    version: "3.4"
    services:
      synse-server:
        container_name: synse-server
        image: vaporio/synse-server:2.0.0
        ports:
          - 5000:5000
        healthcheck:
          test: ["CMD", "bin/ok.sh"]
          interval: 1m
          timeout: 5s
          retries: 3
          start_period: 5s

.. note::

    The ``healthcheck`` option is supported in compose file versions 2.1+, but the
    ``start_period`` option is only supported in compose file versions 3.4+. For more,
    see the `healthcheck reference <https://docs.docker.com/compose/compose-file/#healthcheck>`_.


This can be run with ``docker-compose -f compose.yml up -d``. Then, checking the state, you should see
something similar to

.. code-block:: console

    $ docker ps
    CONTAINER ID        IMAGE                  COMMAND             CREATED              STATUS                        PORTS                    NAMES
    4dd14ab5b25a        vaporio/synse-server   "bin/synse.sh"      About a minute ago   Up About a minute (healthy)   0.0.0.0:5000->5000/tcp   synse-server

*Note the (healthy) state specified under the STATUS output.*

You can use ``docker insepect <container>`` to get more details on the health check. This is
especially useful if the health check is failing or stuck.


