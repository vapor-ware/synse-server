===============
Troubleshooting
===============

This section contains information on troubleshooting, common gotchas, and generally things to watch out for.


Testing the Service
-------------------
A good practice is to hit the :ref:`synse-server-test-command` endpoint after starting up a service. It can
also be useful in ensuring that a service is still running. It will only return "ok" if the service is up and
running, but note that an "ok" response from the test endpoint does **not** indicate the lack of errors
elsewhere - it only means that the Flask application within the Docker container is running and that it is reachable.


Raising an Issue
----------------
If you come across an error or issue with Synse Server or just have a question/suggestion about it, please
`raise an issue <https://github.com/vapor-ware/synse-server/issues>`_ for it!

If raising an issue around an error, please include as much context information around it as possible, including
detailed steps on how to reproduce the error.

Gotchas
-------

scan results unavailable on init
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Particularly in cases when there are many devices configured, or where there is high network latency when configuring
LAN Devices, one may observe that the initial startup takes some time and scan results are not available. Synse Server
attempts to enumerate remote devices (e.g. BMCs for IPMI) on init by default, so that it can cache the results for
subsequent commands. As such, the initialization process may take a few minutes.

To help mitigate this, some configuration options have been added around LAN-based devices, both for multi-threaded
device initialization, and deferring scan to a time post-initialization.

If scan results are unavailable for an extended amount of time, or just to validate that there are no errors while
the initial scan takes place, one can examine the logs, as described in the :ref:`synse-server-debugging` section.

