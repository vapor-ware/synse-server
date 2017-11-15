# ------------------------------------------------------------------------
#  \\//
#   \/aporIO - Vapor Synse Tests
#
#  Build and run Vapor Synse tests.
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
    docker-compose --verbose -f $(1) up --build test-container-x64 ;             \
    if [ "$(value TEST_CONTAINER_EXIT_CODE)" != "0" ]; then            \
        docker-compose -f $(1) kill ;                                  \
        exit $(value TEST_CONTAINER_EXIT_CODE) ;                       \
    fi

# -----------------------------------------------
#  Docker / containers and images.
# -----------------------------------------------

ALL_CONTAINER_IDS=$(shell docker ps -aq)

VAPOR_BASE_ID := $(shell docker images --filter reference='vaporio/vapor-endpoint-base*' -q)

VAPOR_CHILD_IMAGES := $(shell \
	if [ ! -z "$(VAPOR_BASE_ID)" ] ; then \
        docker images --filter since=$(VAPOR_BASE_ID) -q ; \
    fi)

VAPOR_CHILD_IDS := $(shell \
	if [ ! -z "$(VAPOR_CHILD_IMAGES)" ] ; then \
	    docker inspect --format={{.Id}} $(VAPOR_CHILD_IMAGES) | awk -F ":" '{print $$2}' | sort -u ; \
	fi)

CONTAINER_IMG_IDS := $(shell \
    if [ ! -z "$(ALL_CONTAINER_IDS)" ] ; then \
        docker inspect --format={{.Id}}-{{.Image}} $(ALL_CONTAINER_IDS) ; \
    fi)

VAPOR_CHILD_CONTAINERS := $(shell \
	containers=() ; \
    for ctr_info in $(CONTAINER_IMG_IDS); do \
        ctr_id=`echo $$ctr_info | awk -F "-" '{print $$1}'` ; \
        img_id=`echo $$ctr_info | awk -F "-" '{print $$2}' | awk -F ":" '{print $$2}'` ; \
        for i in $(VAPOR_CHILD_IDS); do \
            if [[ "$$i" == "$$img_id" ]] ; then \
                containers+=($$ctr_id) ; \
            fi \
        done \
    done ; \
	echo "$${containers[@]}")

VAPOR_CONTAINERS := $(shell docker ps -a | grep 'vaporio/' | awk '{print $$1}')

ALL_VAPOR_CONTAINERS := $(shell \
    containers=(); \
    all="$(VAPOR_CHILD_CONTAINERS) $(VAPOR_CONTAINERS)" ; \
    read -a arr <<<$$all ; \
    for ctr in $${arr[@]} ; do \
        [[ ! "$${containers[@]}" =~ "$$ctr" ]] && containers+=($$ctr) ; \
    done ; \
    echo "$${containers[@]}")

delete-vapor-containers:
	@if [ -z $(shell echo "${ALL_VAPOR_CONTAINERS}" | tr -d ' ') ]; then \
	    echo "No Vapor containers to delete."; \
	else \
	    docker rm $(ALL_VAPOR_CONTAINERS) || true; \
	fi;

# -----------------------------------------------
#  Testing.
# -----------------------------------------------

# Convenience method for running general tests.
define run_test
	make delete-vapor-containers
	$(call START_TEST_CONTAINER,_composefiles/x64/$(1).yml)
	docker-compose -f _composefiles/x64/$(1).yml kill
endef


# -----------------------------------------------
#  x64
# -----------------------------------------------

# PLC
# ....................

test-plc-endpoints-x64:
    echo --- STARTING PLC ENDPOINTS ---
	$(call run_test,test-plc-endpoints)

test-plc-bad-scan-x64:
	$(call run_test,test-plc-bad-scan)

test-plc-scanall-x64:
	$(call run_test,test-plc-scanall)

test-plc-endurance-x64:
	$(call run_test,test-plc-endurance)

test-plc-emulator-x64:
	$(call run_test,test-plc-emulator)

test-plc-devicebus-x64:
	$(call run_test,test-plc-devicebus)


# IPMI
# ....................

test-ipmi-emulator-x64:
	$(call run_test,test-ipmi-emulator)

test-ipmi-endpoints-x64:
	$(call run_test,test-ipmi-endpoints)

test-ipmi-throughput-x64:
	$(call run_test,test-ipmi-emulator-throughput)

test-ipmi-device-registration-x64:
	$(call run_test,test-ipmi-device-registration)

# Broken #229 (twisted up with graphql)
#test-ipmi-scan-cache-registration-x64:
#	$(call run_test,test-ipmi-scan-cache-registration)

test-ipmi-no-init-scan-x64:
	$(call run_test,test-ipmi-no-init-scan)


# RS485
# ....................

test-rs485-emulator-x64:
	$(call run_test,test-rs485-emulator)

test-rs485-endpoints-x64:
	$(call run_test,test-rs485-endpoints)


# I2C
# ....................

test-i2c-endpoints-x64:
	$(call run_test,test-i2c-endpoints)

test-i2c-devices-x64:
	$(call run_test,test-i2c-devices)


# SNMP
# ....................

test-snmp-emulator-x64:
	$(call run_test,test-snmp-emulator)

test-snmp-device-registration-x64: delete-vapor-containers
	$(call run_test,test-snmp-device-registration)

test-snmp-device-kills-x64: delete-vapor-containers
	$(call run_test,test-snmp-device-kills)

test-snmp-device-kills-force-scan-x64: delete-vapor-containers
	$(call run_test,test-snmp-device-kills-force-scan)


# REDFISH
# ....................

test-redfish-endpoints-x64:
	$(call run_test,test-redfish-endpoints)

test-redfish-endurance-x64:
	$(call run_test,test-redfish-endurance)

test-redfish-emulator-x64:
	$(call run_test,test-redfish-emulator)


# GENERAL
# ....................

test-device-supported-commands-x64:
	$(call run_test,test-device-supported-commands)

# Broken #229. Twisted up with graphql.
#test-endpoint-utils-x64:
#	$(call run_test,test-endpoint-utils)

test-utils-x64:
	$(call run_test,test-utils)

test-location-x64:
	$(call run_test,test-location)


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
	test-ipmi-emulator-x64

# Broken #229	test-ipmi-scan-cache-registration-x64 \

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
	test-snmp-device-kills-force-scan-x64

test-x64-redfish: \
	test-redfish-endpoints-x64 \
	test-redfish-endurance-x64 \
	test-redfish-emulator-x64

test-x64-general: \
	test-utils-x64 \
	test-location-x64 \
	test-device-supported-commands-x64

	# Broken #229: test-endpoint-utils-x64


test-x64: \
	test-x64-plc \
	test-x64-ipmi \
	test-x64-rs485 \
	test-x64-i2c \
	test-x64-snmp \
	test-x64-redfish \
	test-x64-general

test: test-x64
