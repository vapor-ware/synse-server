# ------------------------------------------------------------------------
#  \\//
#   \/aporIO - Vapor OpenDCRE Southbound Tests
#
#  Build and run Vapor OpenDCRE Southbound tests.
#
#  Author: Erick Daniszewski (erick@vapor.io)
#  Date:   01 Nov 2016
# ------------------------------------------------------------------------


SHELL := /bin/bash

# -----------------------------------------------
#  Variables / functions.
# -----------------------------------------------

# This gets the exit code for a docker container named test-container-x64
# that has exited. No evaluation is done, it just hands out the exit code.
TEST_CONTAINER_EXIT_CODE=$(docker ps -a | grep test-container-x64 | \
						 awk '{print $1}' | \
						 xargs docker inspect --format='{{ .State.ExitCode }}')

# This starts the test container with the yml file given at $(1), waits for the
# test container to exit, then gets the container exit code and exits make if
# the exit code is non-zero.
START_TEST_CONTAINER =                                                 \
	docker-compose -f $(1) up --build test-container-x64 ;             \
	if [ "$(value TEST_CONTAINER_EXIT_CODE)" != "0" ] ;                \
		then exit $(value TEST_CONTAINER_EXIT_CODE) ;                  \
	fi


# convenience method for running general tests. these tests do not
# require any sense of "trust"
define run_test
	make delete-containers
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

test-plc-scanall-x64:
	$(call run_test,test_plc_scanall)

test-plc-endurance-x64:
	$(call run_test,test_plc_endurance)

test-plc-emulator-x64:
	$(call run_test,test_plc_emulator)

test-plc-endpointless-x64:
	$(call run_test,test_plc_endpointless)


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


# SUITES
# ....................

test-x64-plc: \
	test-plc-endpoints-x64 \
	test-plc-scanall-x64 \
	test-plc-endurance-x64 \
	test-plc-emulator-x64 \
	test-plc-endpointless-x64


test-x64-ipmi: \
	test-ipmi-endpoints-x64 \
	test-ipmi-throughput-x64 \
	test-ipmi-no-init-scan-x64 \
	test-ipmi-device-registration-x64 \
	test-ipmi-scan-cache-registration-x64 \
	test-ipmi-emulator-x64


test-x64-redfish: \
    test-redfish-endpoints-x64 \
    test-redfish-endurance-x64 \
    test-redfish-emulator-x64


test-x64-general: \
    test-device-supported-commands-x64 \
    test-endpoint-utils-x64


test-x64: \
	test-x64-plc \
	test-x64-ipmi \
	test-x64-redfish \
	test-x64-general


# -----------------------------------------------
# Docker Cleanup
#
# NOTE:
#   these recipes are primarily used in development. caution should
#   be taken when using them, as they are NOT OpenDCRE-specific. they
#   will affect ALL containers/images on the host.
# -----------------------------------------------
RUNNING_CONTAINER_IDS=$(shell docker ps -q)
ALL_CONTAINER_IDS=$(shell docker ps -aq)
DANGLING_IMAGES=$(shell docker images -a -q -f dangling=true)

# untagged images will only have an image id. repository and name are <none>.
ALL_UNTAGGED_IMAGES=$(shell docker images | grep "^<none>" | awk '{print $$3}')
# tagged images will have a repository and tag. The image id may not be unique which causes errors on multiple deletes.
ALL_TAGGED_IMAGES=$(shell docker images | grep -v REPOSITORY | grep -v "^<none>" | awk '{print $$1":"$$2}')

TEST_IMAGES=$(shell docker images | awk '$$1 ~ /test/ { print $$3 }')
LATEST_OLD=$(shell docker images | grep 'latest-old' | awk '{ print $$1":latest-old" }')
DATE_TAG=$(shell docker images | grep '[0-9]\{6\}-[0-9]\{4\}' | awk '{ print $$1":"$$2 }' )

clean-date-tags:
	@if [ -z "$(DATE_TAG)" ]; then echo "No images found with date tags."; else docker rmi $(DATE_TAG); fi;

clean-latest-old:
	@if [ -z "$(LATEST_OLD)" ]; then echo "No latest-old images tagged."; else docker rmi -f $(LATEST_OLD); fi;

stop-containers:
	@if [ -z  "$(RUNNING_CONTAINER_IDS)" ]; then echo "No running containers to stop."; else docker stop $(RUNNING_CONTAINER_IDS); fi;

delete-containers:
	@if [ -z "$(ALL_CONTAINER_IDS)" ]; then echo "No containers to remove."; else docker rm $(ALL_CONTAINER_IDS); fi;

delete-untagged-images:
	@if [ -z "$(ALL_UNTAGGED_IMAGES)" ]; then echo "No untagged images to remove."; else docker rmi -f $(ALL_UNTAGGED_IMAGES); fi;

delete-tagged-images:
	@if [ -z "$(ALL_TAGGED_IMAGES)" ]; then echo "No tagged images to remove."; else docker rmi -f $(ALL_TAGGED_IMAGES); fi;

delete-images: delete-untagged-images delete-tagged-images

delete-test-images:
	@if [ -z "$(TEST_IMAGES)" ]; then echo "No test images to remove"; else docker rmi -f $(TEST_IMAGES); fi;

delete-dangling:
	@if [ -z "$(DANGLING_IMAGES)" ]; then echo "No dangling images to remove."; else docker rmi -f $(DANGLING_IMAGES); fi;

# This cleans up all containers by stopping and removing them.
clean-hard:
	@if [ -z "$(ALL_CONTAINER_IDS)" ]; then echo "No containers to stop and remove."; else docker rm -f $(ALL_CONTAINER_IDS); fi;

# This stops running containers and deletes them. Deletes dangling (unreferenced) images.
clean-volatile: stop-containers delete-containers delete-dangling

# This will clean things up enough to re-test without downloading from docker-hub.
clean-test: clean-hard clean-volatile

delete-all: stop-containers delete-containers delete-images

# Make clean cleans everything up and starts from the beginning,
clean: delete-all
