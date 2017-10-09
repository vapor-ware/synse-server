# ------------------------------------------------------------------------
#  \\//
#   \/aporIO - Synse
#
# Recipes for linting in Synse
# ------------------------------------------------------------------------


.PHONY: source-volume
source-volume:
	docker volume create source


.PHONY: lint
lint: source-volume  ## Lint the Synse Server project files.
	COMMAND='tox -e lint' \
		docker-compose -f compose/lint.yml up \
			--build \
			--abort-on-container-exit \
			--exit-code-from synse-lint

