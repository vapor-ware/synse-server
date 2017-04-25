# ------------------------------------------------------------------------
#  \\//
#   \/aporIO - Vapor Common Tests
#
#  Build and run Vapor Common tests.
#
#  Author: Erick Daniszewski (erick@vapor.io)
#  Date:   06 Dec 2016
# ------------------------------------------------------------------------

test-trust-utils-x64: delete-containers
	docker-compose -f ./_composefiles/x64/test_trust_utils.yml build
	docker-compose -f ./_composefiles/x64/test_trust_utils.yml up test-container-x64
	docker-compose -f ./_composefiles/x64/test_trust_utils.yml stop

test-config-manager-x64: delete-containers
	docker-compose -f ./_composefiles/x64/test_config_manager.yml build
	docker-compose -f ./_composefiles/x64/test_config_manager.yml up test-container-x64
	docker-compose -f ./_composefiles/x64/test_config_manager.yml stop

test-bootstrap-utils-x64: delete-containers
	docker-compose -f ./_composefiles/x64/test_bootstrap_utils.yml build
	docker-compose -f ./_composefiles/x64/test_bootstrap_utils.yml up test-container-x64
	docker-compose -f ./_composefiles/x64/test_bootstrap_utils.yml stop

test-cache-utils-x64: delete-containers
	docker-compose -f ./_composefiles/x64/test_cache_utils.yml build
	docker-compose -f ./_composefiles/x64/test_cache_utils.yml up test-container-x64
	docker-compose -f ./_composefiles/x64/test_cache_utils.yml stop

test-http-x64: delete-containers
	docker-compose -f ./_composefiles/x64/test_http.yml build
	docker-compose -f ./_composefiles/x64/test_http.yml up test-container-x64
	docker-compose -f ./_composefiles/x64/test_http.yml stop


test-all-x64: \
	test-trust-utils-x64 \
	test-config-manager-x64 \
	test-bootstrap-utils-x64 \
	test-cache-utils-x64

# -----------------------------------------------
# Docker Cleanup
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

clean-hard:
	@if [ -z "$(ALL_CONTAINER_IDS)" ]; then echo "No containers to stop and remove."; else docker rm -f $(ALL_CONTAINER_IDS); fi;

clean-volatile: stop-containers delete-containers delete-dangling

delete-all: stop-containers delete-containers delete-images

clean: delete-all
