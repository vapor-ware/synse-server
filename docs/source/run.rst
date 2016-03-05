============================
Running and Testing OpenDCRE
============================

Normally, OpenDCRE may be started and stopped via its built-in OpenMistOS init.d script (``/etc/init.d/opendcre {start|stop|restart}``).

When starting OpenDCRE manually, the following steps may be followed.

- First, OpenDCRE expects a volume to be exposed for logs (``/logs`` is the location within the container, which should be mapped externally). 
- Additionally, OpenDCRE, by default, uses TCP port 5000 to listen for API requests. 
- In cases where the OpenDCRE HAT is used with the OpenDCRE container, the /dev/ttyAMA0 serial device is also required.

With HAT
--------

To start OpenDCRE with the HAT device attached:
::

    docker run -d -p 5000:5000 -v /var/log/opendcre:/logs --device /dev/ttyAMA0:/dev/ttyAMA0 opendcre ./start_opendcre.sh``

With Emulator
-------------

To start OpenDCRE in emulator mode:
::

    docker run -d -p 5000:5000 -v /var/log/opendcre:/logs opendcre ./start_opendcre_emulator.sh

Run Tests
---------

To run the OpenDCRE test suite:
::

    docker run -ti -v /var/log/opendcre:/logs opendcre ./opendcre_southbound/bus-test.py
