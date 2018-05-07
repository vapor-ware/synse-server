#
# Synse Server
#

PKG_NAME := synse
IMG_NAME := vaporio/synse-server
PKG_VER  := $(shell python -c "import synse ; print(synse.__version__)")
DATE     := $(shell date -u +'%Y-%m-%dT%H:%M:%SZ')
export GIT_VER := $(shell /bin/sh -c "git log --pretty=format:'%h' -n 1 || echo 'none'")


HAS_TRANSLATIONS := $(shell find synse -name '*.mo')
HAS_PY36 := $(shell which python3.6 || python -V 2>&1 | grep 3.6 || python3 -V 2>&1 | grep 3.6)
HAS_PIP_COMPILE := $(shell which pip-compile)

# Docker Image tags
DEFAULT_TAGS = ${IMG_NAME}:latest ${IMG_NAME}:${PKG_VER} ${IMG_NAME}:${GIT_VER}
SLIM_TAGS = ${IMG_NAME}:slim ${IMG_NAME}:${PKG_VER}-slim


# Targets to enforce requirements. These are undocumented by `help` as
# they should only be called as target dependencies.

# requires translation files (.mo) to be present
.PHONY: req-translations
req-translations:
ifndef HAS_TRANSLATIONS
	make i18n-compile
endif


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
	tags="" ; \
	for tag in $(SLIM_TAGS); do tags="$${tags} -t $${tag}"; done ; \
	docker build -f dockerfile/slim.dockerfile \
		--build-arg BUILD_DATE=$(DATE) \
		--build-arg BUILD_VERSION=$(PKG_VER) \
		--build-arg VCS_REF=$(GIT_VER) \
		$${tags} .

# build the docker images of synse server with the emulator
.PHONY: docker-default
docker-default:
	tags="" ; \
	for tag in $(DEFAULT_TAGS); do tags="$${tags} -t $${tag}"; done ; \
	docker build -f dockerfile/release.dockerfile \
		--build-arg BUILD_DATE=$(DATE) \
		--build-arg BUILD_VERSION=$(PKG_VER) \
		--build-arg VCS_REF=$(GIT_VER) \
		$${tags} .


# Targets

.PHONY: cover
cover: test-unit ## Run unit tests and open the HTML coverage report
	open ./results/cov-html/index.html

.PHONY: docker
docker: req-translations docker-default docker-slim ## Build the docker image for Synse Server locally

.PHONY: api-doc
api-doc: ## Open the API doc HTML reference
	open ./docs/index.html

.PHONY: docs
docs: clean-docs ## Generate the Synse Server User and API documentation locally
	# User Guide Documentation (see docs/build/html/index.html for output)
	(cd docs; make html)
	# API Documentation (see docs/index.html for output)
	docker build -f docs/Dockerfile -t vaporio/slate-docs docs
	@if [ -d "docs/api/build" ]; then rm -rf docs/api/build; fi;
	docker run --name slate-docs -v `pwd`/docs/api:/source vaporio/slate-docs
	docker cp slate-docs:/slate/build/. docs/api/build
	docker rm slate-docs
	mv docs/api/build/** docs/

.PHONY: clean-docs
clean-docs:  ## Clean all documentation build artifacts
	bin/clean_docs.sh

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
test-unit: pycache-clean req-translations ## Run unit tests
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
test-integration: pycache-clean req-translations ## Run integration tests
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
test-end-to-end: pycache-clean req-translations ## Run end to end tests
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

.PHONY: i18n-extract
i18n-extract:  ## Extract localizable messages from Synse Server source files
	tox -e i18n-extract

.PHONY: i18n-init
i18n-init: i18n-extract  ## Create a new translations catalog
	tox -e i18n-init

.PHONY: i18n-update
i18n-update: i18n-extract  ## Update an existing translations catalog
	tox -e i18n-update

.PHONY: i18n-compile
i18n-compile:  ## Compile translations catalogs into a binary .mo file
	tox -e i18n-compile

.PHONY: version
version: ## Print the version of Synse Server
	@echo "$(PKG_VER)"

.PHONY: help
help:  ## Print Make usage information
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.DEFAULT_GOAL := help
