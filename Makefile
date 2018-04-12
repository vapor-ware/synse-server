#
# Synse Server
#
PKG_NAME := synse
IMG_NAME := vaporio/synse-server
PKG_VER := $(shell python -c "import synse ; print(synse.__version__)")
export GIT_VER := $(shell /bin/sh -c "git log --pretty=format:'%h' -n 1 || echo 'none'")


HAS_PY36 := $(shell which python3.6 || python -V 2>&1 | grep 3.6 || python3 -V 2>&1 | grep 3.6)
HAS_PIP_COMPILE := $(shell which pip-compile)

# Docker Image tags
DEFAULT_TAGS = ${IMG_NAME}:latest ${IMG_NAME}:${PKG_VER} ${IMG_NAME}:${GIT_VER}
SLIM_TAGS = ${IMG_NAME}:slim ${IMG_NAME}:${PKG_VER}-slim


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

# list all the docker image tags for the current build
.PHONY: tags
tags:
	@echo "${DEFAULT_TAGS} ${SLIM_TAGS}"

# pycache-clean is used to clean out .pyc and .pyo files and the __pycache__
# directories from the ./tests directory. This isn't always necessary, but
# the cache will be incorrect if run via container and then locally or vice
# versa. To be safe, we can just clean up with this.
.PHONY: pycache-clean
pycache-clean:
	@find ./tests | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

# build the docker images of synse server without the emulator
.PHONY: docker-slim
docker-slim:
	cp .dockerignore.slim .dockerignore
	tags="" ; \
	for tag in $(SLIM_TAGS); do tags="$${tags} -t $${tag}"; done ; \
	docker build -f dockerfile/release.dockerfile $${tags} .
	rm .dockerignore

# build the docker images of synse server with the emulator
.PHONY: docker-default
docker-default:
	cp .dockerignore.default .dockerignore
	tags="" ; \
	for tag in $(DEFAULT_TAGS); do tags="$${tags} -t $${tag}"; done ; \
	docker build -f dockerfile/release.dockerfile $${tags} .
	rm .dockerignore


# Targets

.PHONY: cover
cover: test-unit ## Run unit tests and open the HTML coverage report
	open ./results/cov-html/index.html

.PHONY: docker
docker: docker-default docker-slim ## Build the docker image for Synse Server locally

.PHONY: api-doc
api-doc: ## Open the API doc HTML reference
	open ./docs/api/build/index.html

.PHONY: docs
docs: ## Generate the Synse Server documentation locally
	docker build -f docs/Dockerfile -t vaporio/slate-docs docs
	@if [ -d "docs/api/build" ]; then rm -rf docs/api/build; fi;
	docker run --name slate-docs -v `pwd`/docs/api:/source vaporio/slate-docs
	docker cp slate-docs:/slate/build/. docs/api/build
	docker rm slate-docs

.PHONY: lint
lint: ## Lint the Synse Server source code
ifdef HAS_PY36
	tox -e lint
else
	@echo "\033[33mpython3.6 not found locally - running linting in container\033[0m"
	docker-compose -f compose/test.yml -f compose/lint.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-test
endif

.PHONY: run
run: docker ## Build and run Synse Server locally (localhost:5000) with emulator
	docker run -d -p 5000:5000 --name synse -e SYNSE_LOGGING=debug ${IMG_NAME} enable-emulator

.PHONY: test
test: pycache-clean test-unit test-integration test-end-to-end ## Run all tests

.PHONY: test-unit
test-unit: pycache-clean ## Run unit tests
ifdef HAS_PY36
	tox tests/unit
else
	@echo "\033[33mpython3.6 not found locally - running tests in container\033[0m"
	docker-compose -f compose/test.yml -f compose/test_unit.yml up \
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
	docker-compose -f compose/test.yml -f compose/test_integration.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-test
endif

.PHONY: test-end-to-end
test-end-to-end: pycache-clean ## Run end to end tests
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

.PHONY: update-deps
update-deps:  ## Update the frozen pip dependencies (requirements.txt)
ifndef HAS_PIP_COMPILE
	pip install pip-tools
endif
	pip-compile --output-file requirements.txt setup.py

.PHONY: translations
translations:  ## (Re)generate the translations.
	tox -e translations

.PHONY: version
version: ## Print the version of Synse Server
	@echo "$(PKG_VER)"

.PHONY: help
help:  ## Print Make usage information
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.DEFAULT_GOAL := help
