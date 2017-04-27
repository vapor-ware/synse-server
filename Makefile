# ------------------------------------------------------------------------
#  \\//
#   \/aporIO - Vapor OpenDCRE Southbound
#
#  Build Vapor OpenDCRE Southbound docker images from the current directory.
#
#  Author: Andrew Cencini (andrew@vapor.io)
#  Date:   01 Sept 2016
# ------------------------------------------------------------------------

PKG_VER := $(shell opendcre_southbound/version.py)
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

build:
	docker build -f dockerfile/Dockerfile.x64 \
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
	$(FPM_OPTS) .

deb: ubuntu1604

el7:
	docker run -it -v $(PWD)/packages:/data vaporio/fpm \
	-t rpm \
	--iteration el7 \
	$(FPM_OPTS) .

rpm: el7

release: deb rpm
	docker run -it -v $(PWD):/data vaporio/hub \
		release create -d \
		-a packages/synse-server-$(PKG_VER)*rpm \
		-a packages/synse-server_$(PKG_VER)*deb \
		-m "v$(PKG_VER)" v$(PKG_VER)

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
