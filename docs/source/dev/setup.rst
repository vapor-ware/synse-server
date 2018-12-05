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
To aid in the developer workflow, Makefile targets are provided for common development
tasks. To see what targets are provided, see the project ``Makefile``, or run ``make help``
out of the project repo root.

.. code-block:: console

    $ make help
    api-doc          Open the API doc HTML reference
    build-docs       Generate the API docs for Synse Server
    cover            Run unit tests and open the HTML coverage report
    docker           Build the docker image for Synse Server locally
    help             Print Make usage information
    lint             Lint the Synse Server source code
    run              Build and run Synse Server locally (localhost:5000) with emulator
    test             Run all tests
    test-end-to-end  Run end to end tests
    test-integration Run integration tests
    test-unit        Run unit tests
    version          Print the version of Synse Server

In general, when developing, tests should be run (e.g. ``make test-unit``) and the code
should be linted (e.g. ``make lint``). This ensures that the code works and is consistent
and readable. Tests should also be added or updated as appropriate (see the Testing section).

Other actions that are useful when developing:

- **build the docker image**: To build a new docker image with the default tags
  (Synse Server version, etc.): ``make docker``
- **test coverage report**: To get a coverage report for the unit tests: ``make cover``
- **documentation**: To build the documentation: ``make build-docs``. To view the
  API docs locally: ``make api-doc``.

CI
---
All commits and pull requests to Synse Server trigger a build on our Jenkins CI server.
The CI configuration can be found in the repo's ``.jenkins`` file. In summary,
a build triggered by a commit will:

- Run unit tests
- Run integration tests
- Run linting

In addition to the above, a build triggered by a pull request merge will:

- Build the docker image
- Push new images out to DockerHub
