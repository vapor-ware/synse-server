Southbound Tests
================

Southbound testing requires docker-compose to run. If you do not have docker-compose:
https://docs.docker.com/compose/install/

The ./test directory contains a collection of various test cases for the southbound
API. Any additional test cases should be added here. These test cases are grouped into
test suites within the vapor_core_southbound directory. (the test suite files have the
naming convention of "test-*.py") Additional test cases should be added to the appropriate
test suite, if one exists. Otherwise, a new test suite should be created.

The ./test directory also contains platform directories (x64, rpi, arm64) which contain the
yaml files for docker-compose configuration. There should be one yaml configuration file
for each test suite that exists (assuming that each test suite uses a separate json config
file for the devicebus emulator).

The ./test/data directory holds the json configuration files for the devicebus emulator. Each
test suite should use one config file, which is passed to the emulator via the yaml config for
that test suite. If adding or changing the data json files, see the 'data-specs.txt' file, as
it describes the board ids allocated to each test case within a test suite.


Running the tests
-----------------

The tests are run from the root directory from the Makefile. Tests can be run for different
devicebus implementations using the recipe:

  $ make test-64-<devicebus impl>

where `<devicebus impl>` is one of 'plc', 'ipmi', 'rs485', or 'i2c'

Additionally, the Makefile contains an option to remove the test containers.

  $ make test-clean-x64

