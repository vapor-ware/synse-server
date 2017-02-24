
.. _opendcre-asset-info-command:

asset information
=================

Get asset information for a given device. The device's ``device_type`` must be of type ``system`` (as reported by
the :ref:`opendcre-scan-command` command). Asset information can consist of board information, chassis information,
and product information.

Request
-------

Format
^^^^^^
.. code-block:: none

    GET /opendcre/<version>/asset/<rack_id>/<board_id>/<device_id>

Parameters
^^^^^^^^^^

:rack_id:
    The id of the rack on which the specified board and device reside.

:board_id:
    Hexadecimal string representation of 4-byte integer value - range 00000000..FFFFFFFF.  Upper byte of
    ``board_id`` reserved for future use in OpenDCRE.  IPMI Bridge board has a special ``board_id`` of 40NNNNNN,
    where NNNNNN corresponds to the hex string id of each configured BMC. For IPMI, the ``board_id`` can also be
    a hostname/ip_address that is associated with the given board.

:device_id:
    The device to read asset information for on the specified board.  Hexadecimal string representation of
    a 2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known
    to OpenDCRE is of type ``system`` - else, a 500 error is returned. For IPMI, the ``device_id`` can also be the
    value of the ``device_info`` field associated with the given device, if present.

Example
^^^^^^^
.. code-block:: none

    http://opendcre:5000/opendcre/1.3/asset/00000001/0004

Response
--------

Schema
^^^^^^

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/opendcre/v1.3/opendcre-1.3-asset-information",
      "title": "OpenDCRE Asset Information",
      "type": "object",
      "properties": {
        "bmc_ip": {
          "type": "string"
        },
        "board_info": {
          "type": "object",
          "properties": {
            "manufacturer": {
              "type": "string"
            },
            "part_number": {
              "type": "string"
            },
            "product_name": {
              "type": "string"
            },
            "serial_number": {
              "type": "string"
            }
          }
        },
        "chassis_info": {
          "type": "object",
          "properties": {
            "chassis_type": {
              "type": "string"
            },
            "part_number": {
              "type": "string"
            },
            "serial_number": {
              "type": "string"
            }
          }
        },
        "product_info": {
          "type": "object",
          "properties": {
            "asset_tag": {
              "type": "string"
            },
            "manufacturer": {
              "type": "string"
            },
            "part_number": {
              "type": "string"
            },
            "product_name": {
              "type": "string"
            },
            "serial_number": {
              "type": "string"
            },
            "version": {
              "type": "string"
            }
          }
        }
      }
    }

.. note::
    Note that the ``bmc_ip`` field is only present for IPMI device asset info.


Example
^^^^^^^

.. code-block:: json

    {
      "bmc_ip": "192.168.1.118",
      "board_info": {
        "manufacturer": "Quanta",
        "part_number": "0001",
        "product_name": "Winterfell",
        "serial_number": "S1234567"
      },
      "chassis_info": {
        "chassis_type": "rack mount chassis",
        "part_number": "P1234567",
        "serial_number": "S1234567"
      },
      "product_info": {
        "asset_tag": "A1234567",
        "manufacturer": "Quanta",
        "part_number": "P1234567",
        "product_name": "Winterfell",
        "serial_number": "S1234567",
        "version": "v1.2.0"
      }
    }

Errors
^^^^^^

:500:
    - asset info is unavailable or does not exist
    - specified device is not of type ``system``
    - invalid/nonexistent ``board_id`` or ``device_id``