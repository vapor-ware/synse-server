# ------------------------------------------------------------------------
#  \\//
#   \/aporIO - OpenDCRE southbound Makefile
#
# Build OpenDCRE docker images from the current directory. Note that
# in order to successfully build with the correct tag, several python
# dependencies are required:
# 	* pyserial		* flask
#	* requests		* lockfile
#	* uwsgi			* docker-compose
#
# Each of the dependencies above may be installed with `pip` on Linux
# and mac. On arm (raspberry pi), lockfile should be installed with
# `easy_install`.
#
# Author: Erick Daniszewski (erick@vapor.io)
#
# Copyright (C) 2015-16  Vapor IO
#
# This file is part of OpenDCRE.
#
# OpenDCRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# OpenDCRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OpenDCRE.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------------------

# get the host's path to the docker binary
DOCKER_PATH = $(shell which docker)

# -----------------------------------------------
# macos (or linux)
# -----------------------------------------------

macos:
	docker build -f Dockerfile.macos -t vaporio/opendcre-southbound-macos .

test-macos-bus: delete-containers
	docker-compose -f ./opendcre_southbound/tests/macos/test_bus.yml build
	docker-compose -f ./opendcre_southbound/tests/macos/test_bus.yml up bus-test-macos
	docker-compose -f ./opendcre_southbound/tests/macos/test_bus.yml stop

test-macos-scanall: delete-containers
	docker-compose -f ./opendcre_southbound/tests/macos/test_scanall.yml build
	docker-compose -f ./opendcre_southbound/tests/macos/test_scanall.yml up scanall-test-macos
	docker-compose -f ./opendcre_southbound/tests/macos/test_scanall.yml stop

test-macos-endurance: delete-containers
	docker-compose -f ./opendcre_southbound/tests/macos/test_endurance.yml build
	docker-compose -f ./opendcre_southbound/tests/macos/test_endurance.yml up endurance-test-macos
	docker-compose -f ./opendcre_southbound/tests/macos/test_endurance.yml stop

test-macos-emulator: delete-containers
	docker-compose -f ./opendcre_southbound/tests/macos/test_emulator.yml build
	docker-compose -f ./opendcre_southbound/tests/macos/test_emulator.yml up emulator-test-macos
	docker-compose -f ./opendcre_southbound/tests/macos/test_emulator.yml stop

test-macos-endpointless: delete-containers
	docker-compose -f ./opendcre_southbound/tests/macos/test_endpointless.yml build
	docker-compose -f ./opendcre_southbound/tests/macos/test_endpointless.yml up endpointless-test-macos
	docker-compose -f ./opendcre_southbound/tests/macos/test_endpointless.yml stop

macos-test: macos test-macos-bus test-macos-scanall test-macos-endurance test-macos-emulator test-macos-endpointless

macos-test-clean:
	docker-compose -f ./opendcre_southbound/tests/macos/test_bus.yml rm -f
	docker-compose -f ./opendcre_southbound/tests/macos/test_scanall.yml rm -f
	docker-compose -f ./opendcre_southbound/tests/macos/test_endurance.yml rm -f
	docker-compose -f ./opendcre_southbound/tests/macos/test_emulator.yml rm -f
	docker-compose -f ./opendcre_southbound/tests/macos/test_endpointless.yml rm -f

# -----------------------------------------------
# rpi
# -----------------------------------------------

rpi:
	docker build -f Dockerfile.rpi -t vaporio/opendcre-southbound-rpi .

# tests not enabled until docker compose supported on OMOS
test-rpi-bus: delete-containers
	docker-compose -f ./opendcre_southbound/tests/rpi/test_bus.yml build
	docker-compose -f ./opendcre_southbound/tests/rpi/test_bus.yml up bus-test-rpi
	docker-compose -f ./opendcre_southbound/tests/rpi/test_bus.yml stop

test-rpi-scanall: delete-containers
	docker-compose -f ./opendcre_southbound/tests/rpi/test_scanall.yml build
	docker-compose -f ./opendcre_southbound/tests/rpi/test_scanall.yml up scanall-test-rpi
	docker-compose -f ./opendcre_southbound/tests/rpi/test_scanall.yml stop

test-rpi-endurance: delete-containers
	docker-compose -f ./opendcre_southbound/tests/rpi/test_endurance.yml build
	docker-compose -f ./opendcre_southbound/tests/rpi/test_endurance.yml up endurance-test-rpi
	docker-compose -f ./opendcre_southbound/tests/rpi/test_endurance.yml stop

test-rpi-emulator: delete-containers
	docker-compose -f ./opendcre_southbound/tests/rpi/test_emulator.yml build
	docker-compose -f ./opendcre_southbound/tests/rpi/test_emulator.yml up emulator-test-rpi
	docker-compose -f ./opendcre_southbound/tests/rpi/test_emulator.yml stop

test-rpi-endpointless: delete-containers
	docker-compose -f ./opendcre_southbound/tests/rpi/test_endpointless.yml build
	docker-compose -f ./opendcre_southbound/tests/rpi/test_endpointless.yml up endpointless-test-rpi
	docker-compose -f ./opendcre_southbound/tests/rpi/test_endpointless.yml stop

rpi-test: rpi test-rpi-bus test-rpi-scanall test-rpi-endurance test-rpi-emulator test-rpi-endpointless

rpi-test-clean:
	docker-compose -f ./opendcre_southbound/tests/rpi/test_bus.yml rm -f
	docker-compose -f ./opendcre_southbound/tests/rpi/test_scanall.yml rm -f
	docker-compose -f ./opendcre_southbound/tests/rpi/test_endurance.yml rm -f
	docker-compose -f ./opendcre_southbound/tests/rpi/test_emulator.yml rm -f
	docker-compose -f ./opendcre_southbound/tests/rpi/test_endpointless.yml rm -f

# -----------------------------------------------
# Docker Cleanup
# -----------------------------------------------
RUNNING_CONTAINER_IDS=$(shell docker ps -q)
ALL_CONTAINER_IDS=$(shell docker ps -aq)
DANGLING_IMAGES=$(shell docker images -a -q -f dangling=true)
ALL_IMAGES=$(shell docker images -q)
TEST_IMAGES=$(shell docker images | awk '$$1 ~ /test/ { print $$3 }')

stop-containers:
	@if [ -z  "$(RUNNING_CONTAINER_IDS)" ]; then echo "No running containers to stop."; else docker stop $(RUNNING_CONTAINER_IDS); fi;

delete-containers:
	@if [ -z "$(ALL_CONTAINER_IDS)" ]; then echo "No containers to remove."; else docker rm $(ALL_CONTAINER_IDS); fi;

delete-images:
	@if [ -z "$(ALL_IMAGES)" ]; then echo "No images to remove."; else docker rmi -f $(ALL_IMAGES); fi;

delete-test-images:
	@if [ -z "$(TEST_IMAGES)" ]; then echo "No test images to remove."; else docker rmi -f $(TEST_IMAGES); fi;

delete-dangling:
	@if [ -z "$(DANGLING_IMAGES)" ]; then echo "No dangling images to remove."; else docker rmi -f $(DANGLING_IMAGES); fi;

delete-all: stop-containers delete-containers delete-images
