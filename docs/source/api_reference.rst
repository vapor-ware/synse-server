.. _opendcre-api-ref:

=============
API Reference
=============

The examples below assume OpenDCRE is running on a given *<ipaddress>* and *<port>*. The default port for OpenDCRE is
TCP port 5000. Currently, all commands are GET requests; a future version will expose these commands via POST as well.

.. note::
    In the API reference information below, there are many references to ``board_id`` and ``device_id`` parameters.
    For IPMI Devices, the values in a board's ``hostnames`` and ``ip_addresses`` fields (e.g. from a
    :ref:`opendcre-scan-command`) can be used in place of the ``board_id``. Additionally, the ``device_info`` field
    for a given device, where specified, can be used in place of its ``device_id``.

    As an example, a device :ref:`opendcre-read-command` for a system temperature device on a board whose (abridged)
    scan information provides us with:

    .. code-block:: json

        {
          "board_id": "40000039",
          "devices": [
            {
              "device_id": "0011",
              "device_info": "System Temp",
              "device_type": "temperature"
            }
          ],
          "hostnames": [
            "kafka001.vapor.io"
          ],
          "ip_addresses": [
            "192.168.1.10"
          ]
        }

    We could formulate a temperature read call in a variety of ways:

    .. code-block:: none

        GET /opendcre/1.3/read/temperature/rack_9/40000039/0011
        GET /opendcre/1.3/read/temperature/rack_9/40000039/System%20Temp
        GET /opendcre/1.3/read/temperature/rack_9/kafka001.vapor.io/0011
        GET /opendcre/1.3/read/temperature/rack_9/kafka001.vapor.io/System%20Temp
        GET /opendcre/1.3/read/temperature/rack_9/192.168.1.10/0011
        GET /opendcre/1.3/read/temperature/rack_9/192.168.1.10/System%20Temp

    As of version 1.3.0, this only works for IPMI Devices, but this functionality will come later for all other devices.


------------

.. include:: api/asset_info.rst

------------

.. include:: api/boot_target.rst

------------

.. include:: api/fan.rst

------------

.. include:: api/host_info.rst

------------

.. include:: api/led.rst

------------

.. include:: api/location.rst

------------

.. include:: api/power.rst

------------

.. include:: api/read.rst

------------

.. include:: api/scan.rst

------------

.. include:: api/service_version.rst

------------

.. include:: api/test.rst

------------

.. include:: api/version.rst

------------

