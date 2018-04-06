#
# Synse Emulator Plugin Deployments
#

.PHONY: tcp
tcp:  ## Spin up the TCP based deployment
	docker-compose -f deploy-tcp.yml up --abort-on-container-exit

.PHONY: unix
unix:  ## Spin up the unix socket based deployment
	docker-compose -f deploy-unix.yml up --abort-on-container-exit

.PHONY: help
help:  ## Print usage information
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.DEFAULT_GOAL := help