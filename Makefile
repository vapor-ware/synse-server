# ------------------------------------------------------------------------
#  \\//
#   \/aporIO - Synse
#
#  Build Vapor Synse docker images from the current directory.
#
#  Author: Andrew Cencini (andrew@vapor.io)
#  Date:   01 Sept 2016
# ------------------------------------------------------------------------

include mk/docker.makefile
include mk/lint.makefile
include mk/package.makefile


PKG_VER := $(shell python synse/__init__.py)
GIT_VER := $(shell /bin/sh -c "git log --pretty=format:'%h' -n 1 || echo 'none'")


run: build
	docker-compose -f compose/emulator.yml up -d

down:
	docker-compose -f compose/emulator.yml -f compose/release.yml down --remove-orphans

# -----------------------------------------------
# Build
# -----------------------------------------------

build:
	docker build -f dockerfile/release.dockerfile \
		-t vaporio/synse-server-internal:latest \
		-t vaporio/synse-server-internal:$(PKG_VER) \
		-t vaporio/synse-server-internal:$(GIT_VER) .



# -----------------------------------------------
#  Variables / functions.
# -----------------------------------------------

# This gets the exit code for a docker container named test-container
# that has exited. No evaluation is done, it just hands out the exit code.
TEST_CONTAINER_EXIT_CODE=$(docker ps -a | grep test-container-x64 | \
						 awk '{print $1}' | \
						 xargs docker inspect --format='{{ .State.ExitCode }}')

# This starts the test container with the yml file given at $(1), waits for the
# test container to exit, then gets the container exit code and exits make if
# the exit code is non-zero.
START_TEST_CONTAINER =                                                 \
	docker-compose --verbose -f $(1) up --build test-container-x64 ;             \
    echo finding config2: ; \
    docker exec x64_synse-test-container_1 /bin/ls -la /synse/override/config.json ; \
	if [ "$(value TEST_CONTAINER_EXIT_CODE)" != "0" ] ;                \
		then exit $(value TEST_CONTAINER_EXIT_CODE) ;                  \
	fi


# convenience method for running general tests. these tests do not
# require any sense of "trust"
define run_test
    echo current_directory is: ${CURDIR}
	make delete-containers
    echo current_directory is: ${CURDIR}
	$(call START_TEST_CONTAINER,synse/tests/_composefiles/x64/$(1).yml)
    echo current_directory is: ${CURDIR}
	docker-compose -f synse/tests/_composefiles/x64/$(1).yml kill
    echo current_directory is: ${CURDIR}
endef


# -----------------------------------------------
#  x64
# -----------------------------------------------

test-%:
	$(call run_test,$@)

# SUITES
# ....................

plc-tests: \
	test-plc-endpoints \
	test-plc-scanall \
	test-plc-endurance \
	test-plc-emulator \
	test-plc-bad-scan \
	test-plc-devicebus

ipmi-tests: \
	test-ipmi-endpoints \
	test-ipmi-emulator-throughput \
	test-ipmi-no-init-scan \
	test-ipmi-device-registration \
	test-ipmi-emulator

# Fails due to https://github.com/vapor-ware/synse-server/issues/229
#	test-ipmi-scan-cache-registration \

rs485-tests: \
	test-rs485-endpoints \
	test-rs485-emulator

i2c-tests: \
	test-i2c-endpoints \
	test-i2c-devices

snmp-tests: \
	test-snmp-emulator \
	test-snmp-device-registration \
	test-snmp-device-kills \
	test-snmp-device-kills-force-scan

redfish-tests: \
    test-redfish-endpoints \
    test-redfish-endurance \
    test-redfish-emulator

general-tests: \
	test-utils \
	test-location \
	test-device-supported-commands

# Fails due to https://github.com/vapor-ware/synse-server/issues/229
#	test-endpoint-utils \

test: \
	plc-tests \
	ipmi-tests \
	rs485-tests \
	i2c-tests \
	snmp-tests \
	redfish-tests \
	general-tests

# Fails due to https://github.com/vapor-ware/synse-server/issues/229
#	graphql-test \

dev: run
	-docker exec -it synse-server /bin/bash

dev-ipmi dev-plc dev-i2c dev-redfish dev-rs485 dev-snmp:
	docker-compose -f compose/$@.yml up -d && docker exec -it synse-server-dev /bin/bash

# Build. Push to DockerHub.
push: build
	docker push vaporio/synse-server-internal:latest
