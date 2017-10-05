
.. _synse-server-version-command:

version
=======

Get version information about a board.

Request
-------

Format
^^^^^^
::

    GET /synse/<version>/version/<rack_id>/<board_id>

Parameters
^^^^^^^^^^

:rack_id:
    The rack id associated with the specified board.

:board_id:
    Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of
    ``board_id`` reserved for future use in Synse Server. IPMI Bridge board has a special ``board_id`` of 40000000.
    For IPMI, the ``board_id`` can also be a hostname/ip_address that is associated with the given board.

Example
^^^^^^^
.. code-block:: none

    http://<host>:5000/synse/1.4/version/00000001

Response
--------

Schema
^^^^^^

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/synse/v1.4/synse-1.4-version",
      "title": "Synse Server Board Version",
      "type": "object",
      "properties": {
        "api_version": {
          "type": "string"
        },
        "firmware_version": {
          "type": "string"
        },
        "synse_version": {
          "type": "string"
        }
      }
    }

Example
^^^^^^^

.. code-block:: json

    {
      "api_version": "1.4",
      "firmware_version": "Synse Server Emulator v1.4.0",
      "synse_version": "1.4.0"
    }

Errors
^^^^^^

:500:
    - version retrieval does not work
    - ``board_id`` specifies a nonexistent board
