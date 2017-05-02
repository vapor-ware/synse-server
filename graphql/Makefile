# ------------------------------------------------------------------------
#  \\//
#   \/aporIO - Vapor GraphQL Frontend API Server
#
#
#  Author: Thomas Rampelberg (thomasr@vapor.io)
#  Date:   24 Feb 2017
# ------------------------------------------------------------------------

define clean
	docker-compose -f compose/test.yml down --remove-orphans
	docker-compose -f compose/release.yml down --remove-orphans
endef

build-test:
	docker-compose -f compose/test.yml build

build-release:
	docker-compose -f compose/release.yml build

test-service:
	docker-compose -f compose/test.yml up -d

dev test: %: build-test test-service real-%
	$(call clean)

real-dev:
	-docker exec -it synse-graphql-test /bin/sh

real-test:
	# Removed the -t on docker exec since Jenkins does not have a tty.
	-docker exec -i synse-graphql-test /bin/sh -c "bin/wait && tox"

clean:
	$(call clean)

run: build-release
	docker-compose -f compose/release.yml up

# meant to be run from within the docker container
one:
	tox -e py36 -- $(test)
