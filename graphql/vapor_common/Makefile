# ------------------------------------------------------------------------
#  \\//
#   \/aporIO - Vapor Common
#
#  Build Vapor Common docker images from the current directory.
#
#  Author: Erick Daniszewski (erick@vapor.io)
#  Date:   12 Jan 2016
# ------------------------------------------------------------------------

# build directive used by vapor-build repo to build services. this should
# not be removed.
build: ;


# -----------------------------------------------
# Docker Cleanup
# -----------------------------------------------
RUNNING_CONTAINER_IDS=$(shell docker ps -q)
ALL_CONTAINER_IDS=$(shell docker ps -aq)
DANGLING_IMAGES=$(shell docker images -a -q -f dangling=true)
ALL_IMAGES=$(shell docker images -q)
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

delete-images:
	@if [ -z "$(ALL_IMAGES)" ]; then echo "No images to remove."; else docker rmi -f $(ALL_IMAGES); fi;

delete-test-images:
	@if [ -z "$(TEST_IMAGES)" ]; then echo "No test images to remove"; else docker rmi -f $(TEST_IMAGES); fi;

delete-dangling:
	@if [ -z "$(DANGLING_IMAGES)" ]; then echo "No dangling images to remove."; else docker rmi -f $(DANGLING_IMAGES); fi;

clean-hard:
	@if [ -z "$(ALL_CONTAINER_IDS)" ]; then echo "No containers to stop and remove."; else docker rm -f $(ALL_CONTAINER_IDS); fi;

clean-volatile: stop-containers delete-containers delete-dangling

delete-all: stop-containers delete-containers delete-images
