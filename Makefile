#
# Synse Server
#

PKG_NAME    := synse-server
PKG_VERSION := $(shell python setup.py --version)
IMAGE_NAME  := vaporio/synse-server

GIT_COMMIT ?= $(shell git rev-parse --short HEAD 2> /dev/null || true)
BUILD_DATE := $(shell date -u +%Y-%m-%dT%T 2> /dev/null)

HAS_TRANSLATIONS := $(shell find synse_server -name '*.mo')
HAS_PY36         := $(shell which python3.6 || python -V 2>&1 | grep 3.6 || python3 -V 2>&1 | grep 3.6)


#
# Utility Targets
#
# Note: these targets are undocumented by `help`, as they are intended to
# only be called as dependencies of other targets.
#

.PHONY: pycache-clean
# pycache-clean is used to clean out .pyc and .pyo files and the __pycache__
# directories from the ./tests directory. This isn't always necessary, but
# the cache will be incorrect if run via container and then locally or vice
# versa. To be safe, we can just clean up with this.
pycache-clean:
	@find ./tests | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: req-translations
# Require translation files (.mo) to be present. If they are not present,
# compile the translations and generate them.
req-translations:
ifndef HAS_TRANSLATIONS
	make i18n
endif


#
# Local Targets
#

.PHONY: api-doc
api-doc:  ## Open the locally generated HTML API reference
	@open ./docs/index.html || echo "${RED}API doc not found locally. To generate, run: 'make docs'${NC}"

.PHONY: clean
clean: pycache-clean  ## Clean up build and test artifacts
	rm -rf build/ dist/ *.egg-info htmlcov/ .coverage* .pytest_cache/ \
		synse_server/__pycache__ synse_server/__pycache__ results/

.PHONY: clean-docs
clean-docs:  ## Clean out the documentation build artifacts
	@bin/clean_docs.sh

.PHONY: cover
cover: test-unit  ## Run unit tests and open their resulting HTML coverage report
	open ./results/cov-html/index.html

.PHONY: deps
deps:  ## Update the frozen pip dependencies (requirements.txt)
	tox -e deps

.PHONY: docker
docker: req-translations  ## Build the docker image locally
	# Build the slim image
	docker build -f dockerfile/synse.dockerfile \
		--label build_date=${BUILD_DATE} \
		--label version=${PKG_VERSION} \
		--label commit=${GIT_COMMIT} \
		--target=slim \
		-t ${IMAGE_NAME}:local-slim \
		-t ${IMAGE_NAME}:latest-slim .

	# Build the full image
	docker build -f dockerfile/synse.dockerfile \
		--label build_date=${BUILD_DATE} \
		--label version=${PKG_VERSION} \
		--label commit=${GIT_COMMIT} \
		-t ${IMAGE_NAME}:local \
		-t ${IMAGE_NAME}:latest .

.PHONY: docs
docs: clean-docs  ## Generate the User Guide and API documentation locally
	@echo "${GREEN}Building User Guide (see docs/build/html/index.html for output)${NC}"
	(cd docs ; make html)

	@echo "${GREEN}Building API Documentation (see docs/index.html for output)${NC}"
	docker build -f docs/Dockerfile -t vaporio/slate-docs docs
	@if [ -d "docs/api/build" ]; then rm -rf docs/api/build; fi;
	docker run --name slate-docs -v `pwd`/docs/api:/source vaporio/slate-docs
	docker cp slate-docs:/slate/build/. docs/api/build
	docker rm slate-docs
	mv docs/api/build/** docs/

.PHONY: github-tag
github-tag:  ## Create and push a tag with the current version
	git tag -a v${PKG_VERSION} -m "${PKG_NAME} version v${PKG_VERSION}"
	git push -u origin v${PKG_VERSION}

.PHONY: i18n
i18n:  ## Update the translations catalog
	tox -e i18n

.PHONY: lint
lint:  ## Run linting checks on the project source code
	tox -e lint

.PHONY: run
run:  ## Run Synse Server with emulator locally (localhost:5000)
	docker run -d \
		-p 5000:5000 \
		-e SYNSE_LOGGING=debug \
		--name synse \
		${IMAGE_NAME} enable-emulator

.PHONY: test
test: pycache-clean test-unit test-integration test-end-to-end  ## Run all tests

.PHONY: test-end-to-end
test-end-to-end: pycache-clean req-translations docker ## Run the end to end tests
ifdef HAS_PY36
	docker-compose -f compose/synse.yml up -d --build
	tox tests/end_to_end
	docker-compose -f compose/synse.yml down
else
	docker-compose -f compose/test.yml -f compose/synse.yml -f compose/test_end_to_end.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-test
	docker-compose -f compose/synse.yml -f compose/test.yml -f compose/test_end_to_end.yml down
endif

.PHONY: test-integration
test-integration: pycache-clean req-translations  ## Run the integration tests
ifdef HAS_PY36
	tox tests/integration
else
	@echo "${YELLOW}python3.6 not found locally - running in container${NC}"
	docker-compose -f compose/test.yml -f compose/test_integration.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-test
endif

.PHONY: test-unit
test-unit: pycache-clean req-translations  ## Run the unit tests
ifdef HAS_PY36
	tox tests/unit
else
	@echo "${YELLOW}python3.6 not found locally - running in container${NC}"
	docker-compose -f compose/test.yml -f compose/test_unit.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-test
endif

.PHONY: version
version: ## Print the version of Synse Server
	@echo "$(PKG_VERSION)"

.PHONY: help
help:  ## Print Make usage information
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.DEFAULT_GOAL := help


#
# CI Targets
#

.PHONY: ci-check-version
ci-check-version:
	PKG_VERSION=$(PKG_VERSION) ./bin/ci/check_version.sh

.PHONY: ci-package
ci-package:
	tox -e dist
