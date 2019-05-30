#
# Synse Server
#

PKG_NAME    := synse-server
PKG_VERSION := $(shell python setup.py --version)
IMAGE_NAME  := vaporio/synse-server

GIT_COMMIT  ?= $(shell git rev-parse --short HEAD 2> /dev/null || true)
BUILD_DATE  := $(shell date -u +%Y-%m-%dT%T 2> /dev/null)


.PHONY: clean
clean:  ## Clean up build and test artifacts
	rm -rf build/ dist/ *.egg-info htmlcov/ .coverage* .pytest_cache/ \
		synse_server/__pycache__ tests/__pycache__

.PHONY: cover
cover: test  ## Run unit tests and open the resulting HTML coverage report
	open ./htmlcov/index.html

.PHONY: deps
deps:  ## Update the frozen pip dependencies (requirements.txt)
	tox -e deps

.PHONY: docker
docker:  ## Build the docker image
	docker build \
		--label build_date=${BUILD_DATE} \
		--label version=${PKG_VERSION} \
		--label commit=${GIT_COMMIT} \
		-t ${IMAGE_NAME}:latest .

.PHONY: fmt
fmt:  ## Automatic source code formatting (isort, autopep8)
	tox -e fmt

.PHONY: github-tag
github-tag:  ## Create and push a tag with the current version
	git tag -a v${PKG_VERSION} -m "${PKG_NAME} version v${PKG_VERSION}"
	git push -u origin v${PKG_VERSION}

.PHONY: i18n
i18n:  ## Update the translations catalog
	tox -e i18n

.PHONY: lint
lint:  ## Run linting checks on the project source code (isort, flake8, twine)
	tox -e lint

.PHONY: test
test:  ## Run the unit tests
	tox tests/unit

.PHONY: version
version:  ## Print the version of Synse Server
	@echo "$(PKG_VERSION)"

.PHONY: help
help:  ## Print Make usage information
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.DEFAULT_GOAL := help
