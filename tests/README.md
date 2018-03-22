# Synse Server Tests
This directory contains the tests for Synse Server. There are currently three
classes of tests:
1. Unit tests
2. Integration tests
3. End to end tests

Each of these test suites are written using [pytest](https://docs.pytest.org/en/latest/)
and can be run from the project root's [Makefile](../Makefile). 

In general, the ***unit tests*** are meant to test small components in isolation, the
***integration tests*** are meant to test Synse Server as a whole with no data (e.g.
emulator plugin) backing, and the ***end to end*** tests are meant to test Synse Server
with an emulator plugin backing.