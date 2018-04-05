.. _debugging:

Debugging
=========

Debug Mode
----------
By default, Synse Server runs with logging set at the ``info`` level. To run it in ``debug``
mode, you can either set ``logging: debug`` in the Synse Server configuration YAML, or set
the ``SYNSE_LOGGING`` environment variable to ``debug``.

The debug environment variable can be set in the docker run command

.. code-block:: console

    docker run -p 5000:5000 -e SYNSE_LOGGING=debug vaporio/synse-server

or via compose file (or other orchestration configuration)

.. code-block:: yaml

    version: "3"
    services:
      synse-server:
        image: vaporio/synse-server
        environment:
          - SYNSE_LOGGING=debug
        ports:
          - 5000:5000


Getting Logs
------------
When running Synse Server in a Docker container, its logs are output to the container's
stdout/stderr, so they can be accessed via ``docker logs``.
