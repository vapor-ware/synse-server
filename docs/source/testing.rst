
.. _synse-server-testing:

=======
Testing
=======

Synse Server has numerous test cases that can be run. Tests must be run from the source
code (see :ref:`synse-server-getting`). All of the tests can be found under the
``synse/tests`` directory.

Tests are made up of four somewhat distinct parts:
    1. The test runner
    2. The test configuration
    3. The test suite
    4. The test cases


Test Runner
^^^^^^^^^^^

In the root of the Synse Server repo, there is a Makefile with targets that will run tests.
All of the tests can be run at once
::

    make test

or subsets of tests can be run, generally grouped by protocol. For example, to run IPMI
tests,
::

    make ipmi-tests

Individual test suites can be run as well by invoking the name of the compose file which
defines that suite as the target name. For example, to run endpoint tests for PLC, which
are defined in ``test-plc-endpoints.yml``,
::

    make test-plc-endpoints

See the Makefile for a full accounting of the test targets.


Test Configuration
^^^^^^^^^^^^^^^^^^

Each test suite is run out of a Docker container. This approach gives us an easy and uniform way to do
unit and integration testing. The tests are orchestrated using docker-compose, and as such, each test
suite requires its own compose file configuration. These compose files can be found in the
``synse/tests/_composefiles`` directory. Below is an example compose file configuration,
followed by a brief explanation.

.. note::
    While this test setup is nice in theory, especially for composing integration and
    end-to-end tests, it can be cumbersome to have to spin up and down containers
    constantly. Work towards an improved testing process is under way for future releases.


.. code-block:: yaml

    version: '3'
    services:
      test-container-x64:
        container_name: test-container-x64
        image: vaporio/synse-server
        build:
          context: ../../../..
          dockerfile: dockerfile/release.dockerfile
        entrypoint: []
        command: bash -c "sleep 5 && python ./synse/tests/test-plc-endpoints.py"
        links:
          - synse-test-container

      synse-test-container:
        image: vaporio/synse-server
        build:
          context: ../../../..
          dockerfile: dockerfile/release.dockerfile
        command: emulate-plc-with-cfg ./synse/emulator/plc/data/test_bus.json
        expose:
          - 5000
        volumes:
          - ../../data/plc_override_config.json:/synse/override/config.json
        environment:
          - VAPOR_DEBUG=true


The example above is taken from an integration tests for Synse Server with a PLC
backing via the PLC emulator. In it, there are two containers that will run.
"test-container-x64" is what runs the actual test suite and "synse-test-container"
is an instance of Synse Server with PLC emulator that will be tested.

.. note::
   All containers which run the actual test cases should be named "test-container-x64",
   since this name is used in the Makefile runner to attach to that container, allowing
   us to see the test results in the console.

Both test container and Synse Server container are built from the same Dockerfile -
this is just for convenience since all of the test dependencies already exist in the
Synse Server image.

The test container runs a test suite after a sleep. Not all tests need a sleep period,
but they are often included to allow Synse Server time to come up and fully configure
before the tests start running against it.

Finally, we set the ``VAPOR_DEBUG`` environment variable to ``true`` - this enables
debug logging. This isn't necessary, but if a test does fail, it makes it easier to
find the root of the failure.


Test Suite
^^^^^^^^^^

As seen above in the compose file, the test suite is defined in the ``synse/tests``
directory. In the same directory, there should be a subdirectory with a name corresponding
to the name of the python file that is the test suite. The subdirectory contains the
test cases which make up the suite. The suite acts only to aggregate and run the test
cases.


Test Cases
^^^^^^^^^^

The test cases are the actual test code that is run. It uses Python's unittest package
to define the tests in the test cases. As mentioned in the previous section, these are
aggregated into a suite for running, so the test cases need not be contained to a single
file, and are in fact often broken up into multiple files for clarity and organization.
