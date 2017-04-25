# ------------------------------------------------------------------------
#  \\//
#   \/aporIO - Vapor GraphQL Frontend API Server
#
#
#  Author: Thomas Rampelberg (thomasr@vapor.io)
#  Date:   24 Feb 2017
# ------------------------------------------------------------------------

image := vaporio/graphql-frontend-x64

build:
	docker-compose -f docker-compose.yml build

# get date for tagging on push
date := $(shell /bin/date "+%m%d%y-%H%M")

dev:
	docker-compose -f docker-compose.yml run --rm test /bin/sh

test:
	docker-compose -f docker-compose.yml run --rm test tox

clean:
	docker-compose -f docker-compose.yml down

run:
	docker-compose -f docker-compose.yml run --service-ports --rm graphql_frontend

# meant to be run from within the docker container
one:
	tox -e py36 -- $(test)
