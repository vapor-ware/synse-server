
.. _synse-server-test-command:

test
====

The test command provides a way to verify that the service is running. It has no dependencies on any
of the configured devicebus interfaces, so it serves only to test that the service is up and reachable
- not that it is configured correctly. The command takes no arguments and, if successful, returns a
status message of "ok".

Request
-------

Format
^^^^^^
.. code-block:: none

   GET  /synse/<version>/test
   POST /synse/<version>/test

Response
--------

Schema
^^^^^^

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/synse/v1.4/synse-1.4-test-status",
      "title": "Synse Server Test Status",
      "type": "object",
      "properties": {
        "status": {
          "type": "string"
        }
      }
    }

Example
^^^^^^^

.. code-block:: json

    {
      "status": "ok"
    }

Errors
^^^^^^

:500:
    - the endpoint is not running