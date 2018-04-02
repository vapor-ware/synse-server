.. _testing:

Testing
=======
The Synse Server repo currently has three types of tests: unit tests, integration tests,
and end to end tests. These tests are found in the ``tests`` directory of the repo under
the subdirectory of the corresponding name.

In general, *unit tests* should test small components, isolated (as best it can be) from
other pieces of code. *Integration tests* should test multiple components of code together.
*End to end tests* test Synse Server as a whole, from endpoint to plugin and back.


Writing Tests
-------------
Whenever additions or changes are made to the code base, there need to be tests that cover
them. Synse Server already has good test coverage, so some changes may not require any tests
to be added.

For most changes or additions, unit tests will need to be added or updated. Those tests are
found in the ``tests/unit`` subdirectory of the project repository. Within that subdirectory,
any additional subdirectory corresponds with the Synse Server python sub-package of the same
name in the ``synse`` directory. Test files should be named ``test_XXX.py`` where ``XXX``
is the name of the corresponding Synse Server file which contains the code being tested.

Tests are written using the `pytest <https://docs.pytest.org/en/latest/>`_ framework.


Running Tests
-------------
There are a variety of ways that tests can be run. If all package and testing dependencies
are met locally, they can be run directly with ``pytest``. While possible, we do not
expect anyone to install all of the Synse Server and testing dependencies into their local
environment.

To keep things clean and repeatable, we use `tox <https://tox.readthedocs.io/en/latest/>`_ as
our primary test runner, along with plugins to get coverage and profiling information.

The tox file is set up so that you only need to specify the directory of the tests in order to
run them. For example, to run unit tests,

.. code-block:: none

    tox tests/unit

As mentioned in the Developer Setup section, Synse Server requires Python 3.6 to run. As an
extension of that, the tests for Synse Server require Python 3.6 to run. If Python 3.6 is not
installed locally, ``tox`` will not be able to set up the virtual environment needed for testing.

You could install Python 3.6, but for convenience Synse Server can also be tested out of
Docker containers (though not necessarily recommended, because it is slower). The compose files
defining the setup for these tests are found in the ``compose`` directory of the project repo.

All of this has been tied together into the Makefile targets for testing to make things
easier. Namely, if Python 3.6 exists, run the tests locally with ``tox``. If not, run them
in via Docker Compose.

All tests can be run with

.. code-block:: bash

    make test

Or, each group of tests can be run individually,

.. code-block:: bash

    # unit tests
    make test-unit

    # integration tests
    make test-integration

    # end to end tests
    make test-end-to-end

The test output will be displayed in the console. Test artifacts will also be generated.


Test Artifacts
--------------
