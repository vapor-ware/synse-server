
.. _synse-server-host-info-command:

host information
================

Get the hostname(s) and IP address(es) for a given host. The device's ``device_type`` should be of type ``system``
(as reported by the :ref:`synse-server-scan-command` command).

Request
-------

Format
^^^^^^
.. code-block:: none

   GET /synse/<version>/host_info/<rack_id>/<board_id>/<device_id>

Parameters
^^^^^^^^^^

:rack_id:
    The id of the rack upon which the specified board and device reside.

:board_id:
    Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of
    ``board_id`` reserved for future use in Synse Server.  IPMI Bridge board has a special ``board_id`` of 40NNNNNN, where
    NNNNNN corresponds to the hex string id of each configured BMC. For IPMI, the ``board_id`` can also be
    a hostname/ip_address that is associated with the given board.

:device_id:
    The device to issue host info control command to on the specified board.  Hexadecimal string representation of
    2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to
    Synse Server is ``system`` - else, a 500 error is returned. For IPMI, the ``device_id`` can also be the
    value of the ``device_info`` field associated with the given device, if present.


Example
^^^^^^^
.. code-block:: none

    http://<host>:5000/synse/1.4/host_info/00000001/0001

Response
--------

Schema
^^^^^^

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/synse/v1.4/synse-1.4-host-information",
      "title": "Synse Server Host Information",
      "type": "object",
      "properties": {
        "hostnames": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "ip_addresses": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      }
    }

Example
^^^^^^^

.. code-block:: json

    {
      "hostnames": [
        "cassandra000"
      ],
      "ip_addresses": [
        "10.10.1.16"
      ]
    }

Errors
^^^^^^

:500:
    - host info action fails
    - specified device is not of type ``system``
    - invalid/nonexistent ``board_id`` or ``device_id``
