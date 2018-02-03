
PKG_NAME := synse
IMG_NAME := vaporio/synse-server2
PKG_VER := $(shell python synse/__init__.py)
export GIT_VER := $(shell /bin/sh -c "git log --pretty=format:'%h' -n 1 || echo 'none'")


# Package

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


# Build

.PHONY: build
build:
	docker build -f dockerfile/release.dockerfile \
	    -t ${IMG_NAME}:latest \
	    -t ${IMG_NAME}:${PKG_VER} \
	    -t ${IMG_NAME}:${GIT_VER} .

.PHONY: run
run: build
	docker run -d -p 5000:5000 --name synse2 ${IMG_NAME} enable-emulator


.PHONY: docs
docs:
	docker build -f docs/build/Dockerfile -t vaporio/slate-docs docs/build
	docker run --name slate-docs -v `pwd`/docs/build/src:/source vaporio/slate-docs
	docker cp slate-docs:/slate/build/. docs
	docker rm slate-docs

# Dev

.PHONY: dev
dev:
	docker-compose -f compose/dev.yml up -d --build
	-docker exec -it synse-dev /bin/sh
	docker-compose -f compose/dev.yml down

# Lint

.PHONY: lint
lint:
	docker-compose -f compose/lint.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-lint


# Test

.PHONY: test
test: utest itest

## unit tests
utest:
	docker-compose -f compose/unit_test.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-test

## integration tests
itest:
	docker-compose -f compose/integration_test.yml up \
	    --build \
	    --abort-on-container-exit \
	    --exit-code-from synse-test


.PHONY: cover
cover: utest
	open ./results/cov-html/index.html
