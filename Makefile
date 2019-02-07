#
# Synse Server
#

PKG_NAME    := synse-server
PKG_VERSION := $(shell python setup.py --version)
IMAGE_NAME  := vaporio/synse-server

GIT_COMMIT ?= $(shell git rev-parse --short HEAD 2> /dev/null || true)
BUILD_DATE := $(shell date -u +%Y-%m-%dT%T 2> /dev/null)


.PHONY: api-doc
api-doc:  ## Open the locally generated HTML API reference
	@open ./docs/index.html || echo "API doc not found locally. To generate, run: 'make docs'"

.PHONY: clean
clean:  ## Clean up build and test artifacts
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
docker:  ## Build the docker image locally
	# Build the slim image
	docker build \
		--label build_date=${BUILD_DATE} \
		--label version=${PKG_VERSION} \
		--label commit=${GIT_COMMIT} \
		--target=slim \
		-t ${IMAGE_NAME}:local-slim \
		-t ${IMAGE_NAME}:latest-slim .

	# Build the full image
	docker build \
		--label build_date=${BUILD_DATE} \
		--label version=${PKG_VERSION} \
		--label commit=${GIT_COMMIT} \
		-t ${IMAGE_NAME}:local \
		-t ${IMAGE_NAME}:latest .

.PHONY: docs
docs: clean-docs  ## Generate the User Guide and API documentation locally
	@echo "Building User Guide (see docs/build/html/index.html for output)"
	(cd docs ; make html)

	@echo "Building API Documentation (see docs/index.html for output)"
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
test: test-unit test-integration test-end-to-end  ## Run all tests

.PHONY: test-end-to-end
test-end-to-end: docker ## Run the end to end tests
	docker-compose -f compose/synse.yml up -d --build
	tox tests/end_to_end
	docker-compose -f compose/synse.yml down

.PHONY: test-integration
test-integration:  ## Run the integration tests
	tox tests/integration

.PHONY: test-unit
test-unit:  ## Run the unit tests
	tox tests/unit

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
