
.. _synse-server-service-version-command:

service version
===============

The service version command identifies the version of the Synse Server instance being queried.
Since the JSON API commands include the API version in the URI, this endpoint provides a means
of getting that version if it is otherwise unknown.

Request
-------

Format
^^^^^^
.. code-block:: none

    GET /synse/version

Response
--------

Schema
^^^^^^

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/synse/v1.4/synse-1.4-service-version",
      "title": "Synse Server Service Version",
      "type": "object",
      "properties": {
        "version": {
          "type": "string"
        }
      }
    }

Example
^^^^^^^

.. code-block:: json

    {
      "version": "1.4"
    }

Errors
^^^^^^

:500:
    - the endpoint is not running

