.. _opendcre-getting:

================
Getting OpenDCRE
================

OpenDCRE's source can be found on `GitHub <https://github.com/vapor-ware/OpenDCRE>`_, where the OpenDCRE Docker image
will need to be built. Alternatively, a pre-built OpenDCRE image can be downloaded from
`DockerHub <https://hub.docker.com/r/vaporio/opendcre/>`_.

.. _opendcre-build-from-source:

Building from Source
--------------------

Once the OpenDCRE source code is downloaded (either via git clone, or downloaded zip), a Docker image can be built.
No additional changes are required to the source for a complete, functioning image, but customizations can be included
in the image, e.g. the inclusion of site-specific TLS certificates, nginx configurations for authn/authz, etc.

The included dockerfile can be used to package up the distribution:
::

    docker build -t opendcre:custom-v1.3.0 -f dockerfile/Dockerfile.x64 .

A Makefile recipe also exists to build the OpenDCRE image and tag it as ``vaporio/opendcre-<arch>:1.3``, where *<arch>*
specifies the architecture (e.g., x64). For the *x64* architecture, this recipe is:
::

    make x64

If building a custom image, apply whatever tag is most descriptive for that image.

At this point, OpenDCRE can be tested (see :ref:`opendcre-testing`) and run (see :ref:`opendcre-running`) to ensure
the build was successful.


Downloading from DockerHub
--------------------------

If no changes are needed to the source, the pre-packed version can be used. It can be downloaded from DockerHub simply
with
::

    docker pull vaporio/opendcre:1.3.0


Updating
--------

Updating OpenDCRE is as simple as building a new image from source, or pulling a new image down from DockerHub.
