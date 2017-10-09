
.. _synse-server-boot-target-command:

boot target
===========

The boot target command may be used to get or set the boot target for a given device (whose device_type must be
``system``).  The boot_target command takes two required parameters - ``board_id`` and ``device_id``, to identify
the device to direct the boot_target command to.  Additionally, a third, optional parameter, ``target`` may be used
to set the boot target.

Request
-------

Format
^^^^^^
.. code-block:: none

   GET /synse/<version>/boot_target/<rack_id>/<board_id>/<device_id>[/<target>]

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
    The device to issue boot target command to on the specified board.  Hexadecimal string representation of
    2-byte integer value - range 0000..FFFF.  Must be a valid, existing device, where the ``device_type`` known to
    Synse Server is ``system`` - else, a 500 error is returned. For IPMI, the ``device_id`` can also be the
    value of the ``device_info`` field associated with the given device, if present.

:target:
    *(optional)* Valid target for the boot_target command include:

    - ``hdd`` : boot to hard disk
    - ``pxe`` : boot to network
    - ``no_override`` : use the system default boot target


If a target is not specified, boot_target makes no changes, and simply retrieves and returns the system boot target.
If ``target`` is specified and valid, the boot_target command will return the updated boot target value, as provided
by the remote device.

Example
^^^^^^^
.. code-block:: none

    http://<host>:5000/synse/1.4/boot_target/00000001/0004


Response
--------

Schema
^^^^^^

.. code-block:: json

    {
      "$schema": "http://schemas.vapor.io/synse/v1.4/synse-1.4-boot-target",
      "title": "Synse Server Boot Target",
      "type": "object",
      "properties": {
        "target": {
          "type": "string",
          "enum": [
            "no_override",
            "hdd",
            "pxe"
          ]
        }
      }
    }

Example
^^^^^^^

.. code-block:: json

    {
      "target": "no_override"
    }

Errors
^^^^^^

:500:
    - boot target action fails
    - specified device is not of type ``system``
    - invalid/nonexistent ``board_id`` or ``device_id``
