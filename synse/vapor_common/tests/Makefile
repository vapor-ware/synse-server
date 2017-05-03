# ------------------------------------------------------------------------
#  \\//
#   \/aporIO - Vapor Common Tests
#
#  Build and run Vapor Common tests.
#
#  Author: Erick Daniszewski (erick@vapor.io)
#  Date:   06 Dec 2016
# ------------------------------------------------------------------------

# Include common functionality to fail make on test failure.
include ../../make_test_common

# Include common functionality for docker cleanup.
include ../../make_docker_common

# Include top level Makefile to get the package information.
include ../../Makefile

# Test if the package file exists.
# If not, move up to the repo root and build it.
# Copy to the tests directory where docker will add it.
# $1 is the PACKAGE_NAME, example vapor_common
# $2 is the PACKAGE_SDIST_FILE from the top level Makefile, example vapor_common-1.0.tar.gz
MAKE_PACKAGE=\
    if [ ! -f $(2) ] ; then \
        echo building package $(1) ; \
        cd ../../ ; make build-package ; \
        ./copy_files_for_testing.sh ; \
    fi

# convenience method for running general tests. these tests do not
# require any sense of "trust"
define run_test
	make delete-vapor-containers
	$(call MAKE_PACKAGE,${PACKAGE_NAME},${PACKAGE_SDIST_FILE})
	$(call START_TEST_CONTAINER,_composefiles/x64/$(1).yml)
	docker-compose -f _composefiles/x64/$(1).yml kill
endef

test-package-setup-x64: delete-vapor-containers
	$(call run_test,test_package_setup)

test-config-manager-x64: delete-vapor-containers
	$(call run_test,test_config_manager)

test-http-x64: delete-vapor-containers
	$(call run_test,test_http)

# Test everything on the x64 platform.
# Please make sure test-package-setup-x64 is first as it tests the pakage setup.
test-all-x64: \
	test-package-setup-x64 \
	test-config-manager-x64 \
	test-http-x64

# Test everything on all supported platforms.
test-all: test-all-x64

# Alias for test-all.
test: test-all

# Want to finish packaging before this is unified.
# The test makefile is in different directories in every repo.
# Some repos have more than one test makefile.
# distutils also wants the tests in <repo_root>/tests and we don't
# have that yet.
delete-packages:
	cd ../../ ; ./clean_files.sh

# Cleanup before a test run.
# For this makefile we only need to delete the packages since
# make delete-vapor-containers is called first in run_test.
clean-test: delete-packages

# Clean up all vapor containers, vapor images, and delete packages.
clean: clean-docker delete-packages
