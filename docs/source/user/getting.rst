.. _getting:

Getting Synse Server
====================

Docker Image
------------
Pre-built Synse Server images can be installed from `DockerHub <https://hub.docker.com/r/vaporio/synse-server/>`_ with

.. code-block:: none

    docker pull vaporio/synse-server

See the repo for the latest tags. In general, the image tags should follow the pattern of

* ``latest`` - The latest release version of Synse Server
* ``edge`` - The latest build of Synse Server out of the master branch. This is not guaranteed
  to be stable.
* ``X.Y.Z`` - The full major.minor.micro release version of Synse Server
* ``slim`` - A slimmed down version of ``latest``. This does not include the built-in emulator.
* ``latest-slim`` - A slimmed down version of ``latest``. This does not include the built-in emulator.
* ``edge-slim`` - A slimmed down version of ``edge``. This does not include the built-in emulator.
* ``X.Y.Z-slim`` - A slimmed down version of ``X.Y.Z``. This does not include the built-in emulator.


Source Code
-----------
The Synse Server source code lives on `GitHub <https://github.com/vapor-ware/synse-server>`_. From here,
it can either be built into a Docker image, or installed locally.
It is recommended to be built as a Docker image. Typically, you would only need
to build from source if you were making your own modifications; if you do not need
to modify Synse Server, you can use a pre-built image from DockerHub (see above).

The Synse Server Dockerfile lives in the repo as ``dockerfile/release.dockerfile``. This
image can be built using the current version tags using the included ``make`` target *(note:
using the current version tags for a custom build is not recommended, as it could
be overwritten when pulling an official image from DockerHub)*.

.. code-block:: none

    make docker

A custom tag can be used as well

.. code-block:: none

    docker build -f dockerfile/release.dockerfile -t my/custom:tag


python install
--------------
Synse Server can be installed onto your local system directly from the repo. The package is not
currently hosted in PyPi, so you must have a clone of the repo. In the repo root, you can simply
run

.. code-block:: none

    python setup.py install

and Synse Server will be installed locally as the ``synse`` package.


Updating
--------
Updating Synse Server is as simple as pulling a new image from DockerHub or building a new image
from source. Since it is not hosted on PyPi, updating a Synse Server python package must be done
manually.
