.. _synse-server-debugging:

=========
Debugging
=========

In the case of failures or errors, it is helpful to know how some basic debugging steps.


Logging
-------
Synse Server logs are output to the container's stdout/stderr. As such, they can be
accessed using ``docker logs``. In addition to the Synse application logging out,
the Nginx and uwsgi server also log out to the same location.

Logs for a given component are prefaced with the name of that component, e.g. for
Nginx, ``nginx |`` - this makes it easier to see the logs for the components
individually. Where ``docker logs synse-server`` (assuming the container is named
synse-server) would get logs for everything,

- ``docker logs synse-server | grep "synse |"`` would give logs for the Synse Flask application
- ``docker logs synse-server | grep "nginx |"`` would give logs for Nginx
- ``docker logs synse-server | grep "uwsgi |"`` would give logs for uWSGI


Enabling Debug Logging
----------------------
By default, production logging is enabled (logging at an ERROR level). To run things in "debug" mode, where DEBUG level
logs are collected, simply run the container with the environment variable ``VAPOR_DEBUG`` set to ``true``. This can be
done in the docker command
::

    docker run -p 5000:5000 -e VAPOR_DEBUG=true vaporio/synse-server

or via composefile
::

    synse-server:
      image: vaporio/synse-server
      ports:
        - 5000:5000
      environment:
        - VAPOR_DEBUG=true

