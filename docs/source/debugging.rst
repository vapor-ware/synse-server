.. _opendcre-debugging:

=========
Debugging
=========

In the case of OpenDCRE failures or errors, it is helpful to know how some basic debugging steps.


Startup Errors
--------------
As covered in the subsequent sections here, OpenDCRE logs out to files within the container. One exception to this
is for errors on container startup. In addition to logging out to file, it logs out to stderr of the container
(pid 1), so it is accessible via ``docker logs``. If a startup error should occur, the OpenDCRE container should
terminate. In this case, it is often prudent to check the docker logs first to see if there is any information
pertaining to a startup error.
::

    docker logs opendcre

A startup error likely will only happen if there is a serious misconfiguration, or if building a custom OpenDCRE image,
something was changed to break the initialization process.


Enabling Debug Logging
----------------------
By default, production logging is enabled (logging at an ERROR level). To run things in "debug" mode, where DEBUG level
logs are collected, simply run the container with the environment variable ``VAPOR_DEBUG`` set to ``true``. This can be
done in the docker command
::

    docker run -p 5000:5000 -e VAPOR_DEBUG=true vaporio/opendcre

or via composefile
::

    opendcre:
      image: vaporio/opendcre
      ports:
        - 5000:5000
      environment:
        - VAPOR_DEBUG=true

With debug logging enabled, there will be two sets of logs captured -- the error logs (same as the production logs), and
the debug logs.

Examining Log Files
-------------------
There are two primary methods for accessing a container's logs: ``docker exec`` and ``docker cp``.

docker exec
^^^^^^^^^^^

Using ``docker exec`` requires the container to be running. If the container has terminated and you need to get at the
logs, this is not the method that should be used. To exec into a container interactively,
::

    docker exec -ti <name or id of container> /bin/bash

This will drop you into the working directory of the container, ``/opendcre``. From there, navigate to ``/logs``, where
all of the container logs are kept.

docker cp
^^^^^^^^^

Using ``docker cp`` can be done when the container is running or when it has terminated. It is used to copy the logs
from the container file system to the host file system.
::

    docker cp <name or id of container>:/logs <host copy destination>

This will place the log files on the host system at the specified location.
