
.. _opendcre-testing:

=======
Testing
=======

OpenDCRE is well-tested with hundreds of test cases that can be run. OpenDCRE tests must be run from the source
code (see :ref:`opendcre-getting`). All of the tests can be found under the ``opendcre_southbound/tests`` directory.

OpenDCRE tests are made up of four somewhat distinct parts:
    1. The test runner
    2. The test configuration
    3. The test suite
    4. The test cases

Test Runner
^^^^^^^^^^^

In ``opendcre_southbound/tests``, there is a Makefile -- this is the test runner. The Makefile contains recipes
to run all of the tests OpenDCRE has. Tests can be run at a suite-level, or in groups of suites (e.g. all tests, tests
for a given devicebus type, etc). Running all OpenDCRE tests is as simple as
::

    make test-x64

Testing for only a single devicebus type can be done by adding the device type suffix, e.g. for PLC
::

    make test-x64-plc

for IPMI
::

    make test-x64-ipmi

and for Redfish
::

    make test-x64-redfish

See the Makefile for more recipes and more information about how to run the tests.


Test Configuration
^^^^^^^^^^^^^^^^^^

Each test in OpenDCRE is run out of a Docker container -- fitting, since OpenDCRE runs out of a Docker container. This
gives us an easy and uniform way to do unit testing and integration testing. The tests are orchestrated using
docker-compose, and as such, each test suite will need to have its own compose file configuration. These compose files
can be found in the ``opendcre_southbound/tests/_composefiles`` directory. Below is an example composefile configuration,
followed by a brief explanation.

.. code-block:: yaml

    test-container-x64:
      container_name: test-container-x64
      build: ../../../..
      dockerfile: Dockerfile.x64
      command: bash -c "sleep 15 && python ./opendcre_southbound/tests/test-plc-endpoints.py"
      links:
        - opendcre-southbound-test-container

    opendcre-southbound-test-container:
      build: ../../../..
      dockerfile: Dockerfile.x64
      command: ./start_opendcre_plc_emulator.sh ./opendcre_southbound/emulator/plc/data/test_bus.json
      expose:
        - 5000
      volumes:
        - ../../data/plc_override_config.json:/opendcre/override/config.json
      environment:
        - VAPOR_DEBUG=true

In the example above, we are performing an integration test on the OpenDCRE REST API with PLC backing (via the PLC
emulator). In it, we have two containers that will run, "test-container-x64", the container that will run the actual
test suite, and "opendcre-southbound-test-container", the OpenDCRE instance running with the PLC emulator backing.

.. note::
   All containers which run the actual test cases should be named "test-container-x64", since this name is
   used in the Makefile runner to attach to that container, allowing us to see the test results in the console.

Both test container and OpenDCRE container are built from the same Dockerfile - this is just for convenience since
all of the test dependencies already exist in the OpenDCRE image.

The test container runs a test suite after a sleep. Not all tests need a sleep period, but they are often included
to allow OpenDCRE to come up and fully configure before the tests start running against it.

Finally, we set the ``VAPOR_DEBUG`` environment variable to ``true`` - this enables debug logging in OpenDCRE. This
isn't necessary, but if a test does fail, it makes it eaiser to find the root of the failure.


Test Suite
^^^^^^^^^^

As seen above in the compose file, the test suite is defined in the ``opendcre_southbound/tests`` directory. In the same
directory, there should be a subdirectory with a name corresponding to the name of the python file that is the test suite.
The subdirectory contains the test cases which make up the suite. The suite acts only to aggregate and run the test
cases.


Test Cases
^^^^^^^^^^

The test cases are the actual test code that is run. It uses Python's unittest package to define the tests in the
test cases. As mentioned in the previous section, these are aggregated into a suite for running, so the test cases
need not be contained to a single file, and are in fact often broken up into multiple files for clarity and organization.
