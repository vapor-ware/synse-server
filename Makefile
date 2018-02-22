#
# Synse Server
#
PKG_NAME := synse
IMG_NAME := vaporio/synse-server
PKG_VER := $(shell python synse/__init__.py)
export GIT_VER := $(shell /bin/sh -c "git log --pretty=format:'%h' -n 1 || echo 'none'")


# Packaging
# Note: these are not documented via `make help` yet

.PHONY: pip-package
pip-package:
	python setup.py sdist

.PHONY: pip-install
pip-install:
	pip install --no-deps -I -e .

.PHONY: pip-uninstall
pip-uninstall:
	pip uninstall -y ${PKG_NAME}

.PHONY: pip-clean
pip-clean:
	rm -rf dist ${PKG_NAME}.egg-info


# Targets

.PHONY: cover
cover: test-unit ## Run unit tests and open the HTML coverage report
	open ./results/cov-html/index.html

.PHONY: docker
docker: ## Build the docker image for Synse Server locally
	docker build -f dockerfile/release.dockerfile \
	    -t ${IMG_NAME}:latest \
	    -t ${IMG_NAME}:${PKG_VER} \
	    -t ${IMG_NAME}:${GIT_VER} .

.PHONY: docs
docs: ## Generate the API docs for Synse Server
	docker build -f docs/build/Dockerfile -t vaporio/slate-docs docs/build
	docker run --name slate-docs -v `pwd`/docs/build/src:/source vaporio/slate-docs
	docker cp slate-docs:/slate/build/. docs
	docker rm slate-docs

.PHONY: lint
lint: ## Lint the Synse Server source code
	docker-compose -f compose/lint.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-lint

.PHONY: run
run: docker ## Build and run Synse Server locally (localhost:5000) with emulator
	docker run -d -p 5000:5000 --name synse -e SYNSE_DEBUG=true ${IMG_NAME} enable-emulator

.PHONY: test
test: test-unit test-integration test-end-to-end ## Run all tests

.PHONY: test-unit
test-unit: ## Run unit tests
	docker-compose -f compose/unit_test.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-test

.PHONY: test-integration
test-integration: ## Run integration tests
	docker-compose -f compose/integration_test.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-test

.PHONY: test-end-to-end
test-end-to-end: ## Run end to end tests
	docker-compose -f compose/end-to-end_test.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-test

.PHONY: version
version: ## Print the version of Synse Server
	@echo "$(PKG_VER)"

.PHONY: help
help:  ## Print Make usage information
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.DEFAULT_GOAL := help