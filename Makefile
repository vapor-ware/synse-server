# ------------------------------------------------------------------------
#  \\//
#   \/aporIO - Synse
#
#  Build Vapor Synse docker images from the current directory.
#
#  Author: Andrew Cencini (andrew@vapor.io)
#  Date:   01 Sept 2016
# ------------------------------------------------------------------------

PKG_VER := $(shell python synse/version.py)
GIT_VER := $(shell /bin/sh -c "git log --pretty=format:'%h' -n 1 || echo 'none'")

FPM_OPTS := -s dir -n synse-server -v $(PKG_VER) \
	--architecture native \
	--url "https://github.com/vapor-ware/synse-server" \
	--license GPL2 \
	--description "IoT sensor management and telemetry system" \
	--maintainer "Thomas Rampelberg <thomasr@vapor.io>" \
	--vendor "Vapor IO" \
	--config-files lib/systemd/system/synse-server.service \
	--after-install synse-server.systemd.postinst

run: build
	docker-compose -f compose/emulator.yml up -d

down:
	docker-compose -f compose/emulator.yml -f compose/release.yml down --remove-orphans

# -----------------------------------------------
# Build
# -----------------------------------------------

# FPM is used to generate the actual packages.
# FIXME: The version is hardcoded right now, should be dynamic.
build-fpm:
	docker build -f dockerfile/fpm.dockerfile \
		-t vaporio/fpm:latest \
		-t vaporio/fpm:1.8.1 .

# hub is used to create the release in github and upload it.
# FIXME: The version is hardcoded right now, should be dynamic.
build-hub:
	docker build -f dockerfile/hub.dockerfile \
		-t vaporio/hub:latest \
		-t vaporio/hub:2.3.0-pre9 .

# packagecloud is used to upload the packages to repos
# FIXME: The version is hardcoded right now, should be dynamic.
build-packagecloud:
	docker build -f dockerfile/packagecloud.dockerfile \
		-t vaporio/packagecloud:latest \
		-t vaporio/packagecloud:0.2.42 .

build:
	docker build -f Dockerfile.x64 \
		-t vaporio/synse-server:latest \
		-t vaporio/synse-server:$(PKG_VER) \
		-t vaporio/synse-server:$(GIT_VER) .

# -----------------------------------------------
# Packages
# -----------------------------------------------

ubuntu1604:
	docker run -it -v $(PWD)/packages:/data vaporio/fpm \
	-t deb \
	--iteration ubuntu1604 \
	--depends "docker-ce > 17" \
	$(FPM_OPTS) .

deb: ubuntu1604

el7:
	docker run -it -v $(PWD)/packages:/data vaporio/fpm \
	-t rpm \
	--iteration el7 \
	--depends "docker-engine > 17" \
	$(FPM_OPTS) .

rpm: el7

release-github:
	docker run -it -v $(PWD):/data vaporio/hub \
		release create -d \
		-a packages/synse-server-$(PKG_VER)*rpm \
		-a packages/synse-server_$(PKG_VER)*deb \
		-m "v$(PKG_VER)" v$(PKG_VER)

release-packagecloud:
	docker run -it -v $(PWD):/data vaporio/packagecloud \
		push VaporIO/synse/el/7 /data/$(shell ls packages/*.rpm)
	docker run -it -v $(PWD):/data vaporio/packagecloud \
		push VaporIO/synse/ubuntu/xenial /data/$(shell ls packages/*.deb)

release: deb rpm release-github release-packagecloud

# -----------------------------------------------
# GraphQL Commands
# -----------------------------------------------
define graphql-clean
	docker-compose -f compose/graphql-test.yml down --remove-orphans
	docker-compose -f compose/graphql-release.yml down --remove-orphans
endef

graphql-build-test:
	docker-compose -f compose/graphql-test.yml build

graphql-build-release:
	docker-compose -f compose/graphql-release.yml build

graphql-test-service:
	docker-compose -f compose/graphql-test.yml up -d

graphql-dev graphql-test: %: graphql-build-test graphql-test-service real-%
	$(call graphql-clean)

real-graphql-dev:
	-docker exec -it synse-graphql-test /bin/sh

real-graphql-test:
	# Removed the -t on docker exec since Jenkins does not have a tty.
	-docker exec -i synse-graphql-test /bin/sh -c "bin/wait && tox"

graphql-clean:
	$(call graphql-clean)

graphql-run: graphql-build-release
	docker-compose -f compose/graphql-release.yml up


# -----------------------------------------------
# Docker Cleanup
#
# NOTE:
#   these recipes are primarily used in development. caution should
#   be taken when using them, as they are NOT Synse-specific. they
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

clean-build-artifacts:
	-rm -f packages/*.deb
	-rm -f packages/*.rpm

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

clean-hard:
	@if [ -z "$(ALL_CONTAINER_IDS)" ]; then echo "No containers to stop and remove."; else docker rm -f $(ALL_CONTAINER_IDS); fi;

clean-volatile: stop-containers delete-containers delete-dangling

delete-all: stop-containers delete-containers delete-images

clean: clean-build-artifacts delete-all
