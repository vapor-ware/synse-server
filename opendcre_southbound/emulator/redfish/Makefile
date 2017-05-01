
# Include common functionality for docker cleanup.
include ../../../../../vapor_common/make_docker_common


redfish-yml:
	docker-compose -f redfish.yml build
	docker-compose -f redfish.yml up redfish-emulator

build-x64:
	docker build -f Dockerfile.x64 -t vaporio/redfish-emulator-x64 .


# get date for tagging on push
date := $(shell /bin/date "+%m%d%y-%H%M")

push-latest-x64:
	docker build -f Dockerfile.x64 -t vaporio/redfish-emulator-x64:$(date) .
	docker tag vaporio/redfish-emulator-x64:$(date) vaporio/redfish-emulator-x64:latest
	docker push vaporio/redfish-emulator-x64:$(date)
	docker push vaporio/redfish-emulator-x64:latest
	curl -X POST --data-urlencode 'payload={"channel": "#checkins", "username": "docker-hub", "text": "Pushed redfish-emulator:latest image to docker hub.", "icon_emoji": ":ghost:"}' https://hooks.slack.com/services/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


push-private-x64:
	docker build -f Dockerfile.x64 -t vaporio/redfish-emulator-x64:$(date) .
	docker tag vaporio/redfish-emulator-x64:$(date) vaporio/redfish-emulator-x64:latest-dev
	docker push vaporio/redfish-emulator-x64:$(date)
	docker push vaporio/redfish-emulator-x64:latest-dev
	curl -X POST --data-urlencode 'payload={"channel": "#checkins", "username": "docker-hub", "text": "Pushed redfish-emulator:latest-dev image to docker hub.", "icon_emoji": ":ghost:"}' https://hooks.slack.com/services/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
