#
# Synse Server
#
PKG_NAME := synse
IMG_NAME := vaporio/synse-server
PKG_VER := $(shell python synse/__init__.py)
export GIT_VER := $(shell /bin/sh -c "git log --pretty=format:'%h' -n 1 || echo 'none'")


HAS_PY36 := $(shell which python3.6 || python -V 2>&1 | grep 3.6 || python3 -V 2>&1 | grep 3.6)


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


# Helper Targets

.PHONY: pycache-clean
# pycache-clean is used to clean out .pyc and .pyo files and the __pycache__
# directories from the ./tests directory. This isn't always necessary, but
# the cache will be incorrect if run via container and then locally or vice
# versa. To be safe, we can just clean up with this.
pycache-clean:
	@find ./tests | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

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
ifdef HAS_PY36
	tox -e lint
else
	@echo "\033[33mpython3.6 not found locally - running linting in container\033[0m"
	docker-compose -f compose/lint.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-lint
endif

.PHONY: run
run: docker ## Build and run Synse Server locally (localhost:5000) with emulator
	docker run -d -p 5000:5000 --name synse -e SYNSE_DEBUG=true ${IMG_NAME} enable-emulator

.PHONY: test
test: pycache-clean test-unit test-integration test-end-to-end ## Run all tests

.PHONY: test-unit
test-unit: pycache-clean ## Run unit tests
ifdef HAS_PY36
	tox tests/unit
else
	@echo "\033[33mpython3.6 not found locally - running tests in container\033[0m"
	docker-compose -f compose/unit_test.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-test
endif

.PHONY: test-integration
test-integration: pycache-clean ## Run integration tests
ifdef HAS_PY36
	tox tests/integration
else
	@echo "\033[33mpython3.6 not found locally - running tests in container\033[0m"
	docker-compose -f compose/integration_test.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-test
endif

.PHONY: test-end-to-end
test-end-to-end: pycache-clean ## Run end to end tests
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