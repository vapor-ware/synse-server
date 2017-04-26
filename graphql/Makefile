# ------------------------------------------------------------------------
#  \\//
#   \/aporIO - Vapor GraphQL Frontend API Server
#
#
#  Author: Thomas Rampelberg (thomasr@vapor.io)
#  Date:   24 Feb 2017
# ------------------------------------------------------------------------

build-test:
	docker-compose -f compose/test.yml build

build-release:
	docker-compose -f compose/release.yml build

dev: build-test
	docker-compose -f compose/test.yml run --rm test /bin/sh

test: build-test
	docker-compose -f compose/test.yml run --rm test tox

clean:
	docker-compose -f compose/test.yml down --remove-orphans
	docker-compose -f compose/release.yml down --remove-orphans
	docker-compose -f compose/emulator.yml down --remove-orphans

run: build-release
	docker-compose -f compose/release.yml up

# meant to be run from within the docker container
one:
	tox -e py36 -- $(test)
