#
# Synse Server
#

PKG_NAME    := synse
PKG_VERSION := $(shell python -c "import synse ; print(synse.__version__)")
IMAGE_NAME  := vaporio/synse-server
IMAGE_TAGS  ?= latest local

HAS_TRANSLATIONS := $(shell find synse -name '*.mo')
HAS_PY36         := $(shell which python3.6 || python -V 2>&1 | grep 3.6 || python3 -V 2>&1 | grep 3.6)
HAS_PIP_COMPILE  := $(shell which pip-compile)

RED    := \033[0;31m
GREEN  := \033[0;32m
YELLOW := \033[0;33m
NC     := \033[0m


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
	make i18n-compile
endif


#
# Local Targets
#

.PHONY: api-doc
api-doc:  ## Open the locally generated HTML API reference
	@open ./docs/index.html || echo "${RED}API doc not found locally. To generate, run: 'make docs'${NC}"

.PHONY: clean
clean: pycache-clean  ## Clean up build/test artifacts
	rm -rf build/ dist/ *.egg-info results/ .coverage* .pytest_cache

.PHONY: clean-docs
clean-docs:  ## Clean out the documentation build artifacts
	@bin/clean_docs.sh

.PHONY: cover
cover: test-unit  ## Run unit tests and open their resulting HTML coverage report
	open ./results/cov-html/index.html

.PHONY: deps
deps:  ## Update the frozen pip dependencies (requirements.txt)
ifndef HAS_PIP_COMPILE
	pip install pip-tools
endif
	pip-compile --output-file requirements.txt setup.py

.PHONY: docker
docker: req-translations  ## Build the docker image locally
	@ IMAGE_TAGS="$(IMAGE_TAGS)" IMAGE_NAME=$(IMAGE_NAME) ./bin/build.sh

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

.PHONY: i18n-compile
i18n-compile:  ## Compile translations catalogs into a binary .mo file
	tox -e i18n-compile

.PHONY: i18n-extract
i18n-extract:  ## Extract localizable messages from Synse Server source files
	tox -e i18n-extract

.PHONY: i18n-init
i18n-init: i18n-extract  ## Create a new translations catalog
	tox -e i18n-init

.PHONY: i18n-update
i18n-update: i18n-extract  ## Update an existing translations catalog
	tox -e i18n-update

.PHONY: lint
lint:  ## Lint the Synse Server source code
ifdef HAS_PY36
	tox -e lint
else
	@echo "${YELLOW}python3.6 not found locally - running in container${NC}"
	docker-compose -f compose/test.yml -f compose/lint.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-test
endif

.PHONY: run
run: docker  ## Build and run Synse Server with emulator locally (localhost:5000)
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
