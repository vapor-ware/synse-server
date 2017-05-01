# ------------------------------------------------------------------------
#  \\//
#   \/aporIO - Vapor OpenDCRE Southbound Tests
#
#  Build and run Vapor OpenDCRE Southbound tests.
#
#  Author: Erick Daniszewski (erick@vapor.io)
#  Date:   01 Nov 2016
# ------------------------------------------------------------------------

# Include common functionality to fail make on test failure.
include ../../../vapor_common/make_test_common

# Include common functionality for docker cleanup.
include ../../../vapor_common/make_docker_common

# Include top level Makefile to get the package information.
#include ../../Makefile

# Include top level Makefile to get the package information.
# Test if the package file exists.
# If not, move up to the repo root and build it.
# Copy to the tests directory where docker will add it.
# $1 is the PACKAGE_NAME, example vapor_common
# $2 is the PACKAGE_SDIST_FILE from the top level Makefile, example vapor_common-1.0.tar.gz
MAKE_PACKAGE=\
    echo MAKE_PACKAGE $(1) $(2) ; \
    if [ ! -f $(2) ] ; then \
        echo building package $(1) ; \
        cd ../../../ ; make build-package ; \
        ./copy_files_for_testing.sh ; \
    fi

# convenience method for running trusted tests. here, certs will be
# mounted into the correct directory, where they will be picked up
# by the container.
define run_trusted
	make delete-vapor-containers
	$(call MAKE_PACKAGE,${PACKAGE_NAME},${PACKAGE_SDIST_FILE})
	export CERT_PATH="/etc/vapor/cert" ; \
	$(call START_TEST_CONTAINER,_composefiles/x64/$(1).yml) ; \
	docker-compose -f _composefiles/x64/$(1).yml kill
endef

# convenience method for running untrusted tests. here, certs will
# be mounted into a container directory such that they will not be
# found by the container, thus it will run in "untrusted" mode.
define run_untrusted
	make delete-vapor-containers
	$(call MAKE_PACKAGE,${PACKAGE_NAME},${PACKAGE_SDIST_FILE})
	export CERT_PATH="/tmp" ; \
	$(call START_TEST_CONTAINER,_composefiles/x64/$(1).yml) ; \
	docker-compose -f _composefiles/x64/$(1).yml kill
endef

# convenience method for running general tests. these tests do not
# require any sense of "trust"
define run_test
	make delete-vapor-containers
	$(call MAKE_PACKAGE,${PACKAGE_NAME},${PACKAGE_SDIST_FILE})
	$(call START_TEST_CONTAINER,_composefiles/x64/$(1).yml)
	docker-compose -f _composefiles/x64/$(1).yml kill
endef


# -----------------------------------------------
#  x64
# -----------------------------------------------

# PLC
# ....................

test-plc-endpoints-x64:
	$(call run_test,test_plc_endpoints)

test-plc-bad-scan-x64:
	$(call run_test,test_plc_bad_scan)

test-plc-scanall-x64:
	$(call run_test,test_plc_scanall)

test-plc-endurance-x64:
	$(call run_test,test_plc_endurance)

test-plc-emulator-x64:
	$(call run_test,test_plc_emulator)

test-plc-devicebus-x64:
	$(call run_test,test_plc_devicebus)


# IPMI
# ....................

test-ipmi-emulator-x64:
	$(call run_test,test_ipmi_emulator)

test-ipmi-endpoints-x64:
	$(call run_test,test_ipmi_endpoints)

test-ipmi-throughput-x64:
	$(call run_test,test_ipmi_emulator_throughput)

test-ipmi-device-registration-x64:
	$(call run_test,test_ipmi_device_registration)

test-ipmi-scan-cache-registration-x64:
	$(call run_test,test_ipmi_scan_cache_registration)

test-ipmi-no-init-scan-x64:
	$(call run_test,test_ipmi_no_init_scan)


# RS485
# ....................

test-rs485-emulator-x64:
	$(call run_test,test_rs485_emulator)

test-rs485-endpoints-x64:
	$(call run_test,test_rs485_endpoints)


# I2C
# ....................

test-i2c-endpoints-x64:
	$(call run_test,test_i2c_endpoints)

test-i2c-devices-x64:
	$(call run_test,test_i2c_devices)


# SNMP
# ....................

test-snmp-emulator-x64:
	$(call run_test,test_snmp_emulator)

test-snmp-device-registration-x64: delete-vapor-containers
	$(call MAKE_PACKAGE,${PACKAGE_NAME},${PACKAGE_SDIST_FILE})
	docker-compose -f ./_composefiles/x64/test_snmp_device_registration.yml build
	$(call START_TEST_CONTAINER,./_composefiles/x64/test_snmp_device_registration.yml)
	docker-compose -f ./_composefiles/x64/test_snmp_device_registration.yml stop

test-snmp-device-kills-x64: delete-vapor-containers
	$(call MAKE_PACKAGE,${PACKAGE_NAME},${PACKAGE_SDIST_FILE})
	docker-compose -f ./_composefiles/x64/test_snmp_device_kills.yml build

	# Kill RiZone container and One TestDevice1 container (board1).
	# Here we are just sleeping and killing in the background. If we want to we can
	# hit the test endpoint on OpenDCRE to make sure it's fully up, but the main thing
	# is that device registration goes through before the kill.
	( sleep 25 ; docker kill snmp-emulator-rittal-rizone) &
	( sleep 25 ; docker kill snmp-emulator-opendcre-testdevice1-board1) &

	$(call START_TEST_CONTAINER,./_composefiles/x64/test_snmp_device_kills.yml)
	docker-compose -f ./_composefiles/x64/test_snmp_device_kills.yml stop

test-snmp-device-kills-force-scan-x64: delete-vapor-containers
	$(call MAKE_PACKAGE,${PACKAGE_NAME},${PACKAGE_SDIST_FILE})
	docker-compose -f ./_composefiles/x64/test_snmp_device_kills.yml build

	# Kill RiZone container and One TestDevice1 container (board1).
	# Here we are just sleeping and killing in the background. If we want to we can
	# hit the test endpoint on OpenDCRE to make sure it's fully up, but the main thing
	# is that device registration goes through before the kill.
	( sleep 25 ; docker kill snmp-emulator-rittal-rizone) &
	( sleep 25 ; docker kill snmp-emulator-opendcre-testdevice1-board1) &

	$(call START_TEST_CONTAINER,./_composefiles/x64/test_snmp_device_kills_force_scan.yml)
	docker-compose -f ./_composefiles/x64/test_snmp_device_kills_force_scan.yml stop

test-snmp-rittal-initial-x64: delete-vapor-containers
	$(call MAKE_PACKAGE,${PACKAGE_NAME},${PACKAGE_SDIST_FILE})
	docker-compose -f ./_composefiles/x64/test_snmp_rittal_initial.yml build
	$(call START_TEST_CONTAINER,./_composefiles/x64/test_snmp_rittal_initial.yml)
	docker-compose -f ./_composefiles/x64/test_snmp_rittal_initial.yml stop

# REDFISH
# ....................

test-redfish-endpoints-x64:
	$(call run_test,test_redfish_endpoints)

test-redfish-endurance-x64:
	$(call run_test,test_redfish_endurance)

test-redfish-emulator-x64:
	$(call run_test,test_redfish_emulator)


# GENERAL
# ....................

test-device-supported-commands-x64:
	$(call run_test,test_device_supported_commands)

test-endpoint-utils-x64:
	$(call run_test,test_endpoint_utils)

test-utils-x64:
	$(call run_test,test_utils)

test-location-x64:
	$(call run_test,test_location)


# SUITES
# ....................

test-x64-plc: \
	test-plc-endpoints-x64 \
	test-plc-scanall-x64 \
	test-plc-endurance-x64 \
	test-plc-emulator-x64 \
	test-plc-bad-scan-x64 \
	test-plc-devicebus-x64

test-x64-ipmi: \
	test-ipmi-endpoints-x64 \
	test-ipmi-throughput-x64 \
	test-ipmi-no-init-scan-x64 \
	test-ipmi-device-registration-x64 \
	test-ipmi-scan-cache-registration-x64 \
	test-ipmi-emulator-x64

test-x64-rs485: \
	test-rs485-endpoints-x64 \
	test-rs485-emulator-x64

test-x64-i2c: \
	test-i2c-endpoints-x64 \
	test-i2c-devices-x64

test-x64-snmp: \
	test-snmp-emulator-x64 \
	test-snmp-device-registration-x64 \
	test-snmp-device-kills-x64 \
	test-snmp-device-kills-force-scan-x64 \
	test-snmp-rittal-initial-x64

test-x64-redfish: \
    test-redfish-endpoints-x64 \
    test-redfish-endurance-x64 \
    test-redfish-emulator-x64


test-x64-general: \
	test-utils-x64 \
	test-location-x64 \
	test-device-supported-commands-x64 \
	test-endpoint-utils-x64


test-x64: \
	test-x64-plc \
	test-x64-ipmi \
	test-x64-rs485 \
	test-x64-i2c \
	test-x64-snmp \
	test-x64-redfish \
	test-x64-general

test: test-x64

# Finish packaging before this is unified.
# The test makefile is in different directories in every repo.
# Some repos have more than one test makefile.
# distutils also wants the tests in <repo_root>/tests and we don't
# have that everywhere yet.
delete-packages:
	cd ../../../ ; ./clean_files.sh

# Cleanup before a test run.
# For this makefile we only need to delete the packages since
# make delete-vapor-containers is called first in run_test.
clean-test: delete-packages
