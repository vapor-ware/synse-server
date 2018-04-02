.. _setup:

Developer Setup
===============
This section describes the developer setup and workflow that many of us use when
developing Synse Server at Vapor IO.

Requirements
------------
To develop Synse Server, you will first need the Synse Server code. To get it,
fork the `GitHub repo <https://github.com/vapor-ware/synse-server>`_ and clone it
down to your local workspace.

Synse Server is currently only developed and tested on Python 3.6. While it may
work on other versions of Python, they are not currently actively supported or tested
on other versions. As such, Python 3.6 (either locally, in a development container,
or in a virtual environment) is required.

Other tools and components that are used in development:

- `tox <https://tox.readthedocs.io/en/latest/>`_ for running tests and linting
  (minimum version: 2.9.0).
- `Docker <https://www.docker.com/>`_ for building, running, and managing Docker images
  and containers.
- `Docker Compose <https://docs.docker.com/compose/install/>`_ for building, running, and
  managing local deployments for testing and dev work.
- `GNU Make <https://www.gnu.org/software/make/>`_ for running make targets that make
  building, linting, and testing easier.

Workflow
--------
