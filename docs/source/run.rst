============================
Running and Testing OpenDCRE
============================

When starting OpenDCRE manually, the following steps may be followed.

- First, OpenDCRE expects a volume to be exposed for logs (``/logs`` is the location within the container, which should be mapped externally). 
- Additionally, OpenDCRE, by default, uses TCP port 5000 to listen for API requests. 
- In cases where the OpenDCRE HAT is used with the OpenDCRE container, the ``/dev/ttyAMA0`` serial device is also required.
- In cases where the OpenDCRE HAT is used with the OpenDCRE container, ``/dev/mem`` must also be provided to the container for use by RPI GPIO for modem configuration.
- Finally, in cases where the HAT is used with OpenDCRE, the container must also be set to ``--privileged`` to allow GPIO access.

With HAT
--------

To start OpenDCRE with the HAT device attached:
::

    docker run -d -p 5000:5000 -v /var/log/opendcre:/logs --privileged --device /dev/mem:/dev/mem --device /dev/ttyAMA0:/dev/ttyAMA0 opendcre ./start_opendcre.sh

With Emulator
-------------

To start OpenDCRE in local emulator mode:
::

    docker run -d -p 5000:5000 -v /var/log/opendcre:/logs opendcre ./start_opendcre_emulator.sh

Run Tests
---------

To run the OpenDCRE test suite (from OpenDCRE root directory):
::

    make rpi-test
