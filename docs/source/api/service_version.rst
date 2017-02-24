
.. _opendcre-service-version-command:

service version
===============

The OpenDCRE service version command identifies the version of OpenDCRE running on the OpenDCRE instance being queried.
Since OpenDCRE's REST API commands include the API version in the URI, this endpoint provides a means of getting that
version if it is otherwise unknown.

Request
-------

Format
^^^^^^
.. code-block:: none

    GET /opendcre/version

Response
--------

Schema
^^^^^^

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.3/opendcre-1.3-service-version",
      "title": "OpenDCRE Service Version",
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
      "version": "1.3"
    }

Errors
^^^^^^

:500:
    - the endpoint is not running

