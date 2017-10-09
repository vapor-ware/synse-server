.. _synse-server-getting:

====================
Getting Synse Server
====================

Synse Server's source can be found on `GitHub <https://github.com/vapor-ware/synse-server>`_,
where the Synse Server Docker image can be built. Alternatively, a pre-built
Synse Server image can be downloaded from `DockerHub <https://hub.docker.com/r/vaporio/synse-server/>`_.

.. _synse-server-build-from-source:

Building from Source
--------------------

Once the Synse Server source code is downloaded (either via git clone, or downloaded zip), a Docker image can be built.
No additional changes are required to the source for a complete, functioning image, but customizations can be included
in the image, e.g. the inclusion of site-specific TLS certificates, nginx configurations for authn/authz, etc.

The included dockerfile can be used to package up the distribution:
::

    docker build -t synse-server:custom-img -f dockerfile/release.dockerfile .

A Makefile recipe also exists to build the Synse Server image and tag it with the current version
::

    make build

If building a custom image, apply whatever tag is most descriptive for that image.

At this point, Synse Server can be tested (see :ref:`synse-server-testing`) and run (see :ref:`synse-server-running`)
to ensure the build was successful.


Downloading from DockerHub
--------------------------

If no changes are needed to the source, the pre-packed version can be used. It can be downloaded from DockerHub simply
with
::

    docker pull vaporio/synse-server


Updating
--------

Updating Synse Server is as simple as building a new image from source, or pulling a new image down from DockerHub.
