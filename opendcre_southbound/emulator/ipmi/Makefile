
# Include common functionality for docker cleanup.
include ../../../../../vapor_common/make_docker_common

ipmi-yml:
	docker-compose -f ipmi.yml build
	docker-compose -f ipmi.yml up ipmi-emulator


build-x64:
	docker build -f Dockerfile.x64 -t vaporio/ipmi-emulator-x64 .


# get date for tagging on push
date := $(shell /bin/date "+%m%d%y-%H%M")

push-latest-x64:
	docker build -f Dockerfile.x64 -t vaporio/ipmi-emulator-x64:$(date) .
	docker tag vaporio/ipmi-emulator-x64:$(date) vaporio/ipmi-emulator-x64:latest
	docker push vaporio/ipmi-emulator-x64:$(date)
	docker push vaporio/ipmi-emulator-x64:latest
	curl -X POST --data-urlencode 'payload={"channel": "#checkins", "username": "docker-hub", "text": "Pushed ipmi-emulator:latest image to docker hub.", "icon_emoji": ":ghost:"}' https://hooks.slack.com/services/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


push-private-x64:
	docker build -f Dockerfile.x64 -t vaporio/ipmi-emulator-x64:$(date) .
	docker tag vaporio/ipmi-emulator-x64:$(date) vaporio/ipmi-emulator-x64:latest-dev
	docker push vaporio/ipmi-emulator-x64:$(date)
	docker push vaporio/ipmi-emulator-x64:latest-dev
	curl -X POST --data-urlencode 'payload={"channel": "#checkins", "username": "docker-hub", "text": "Pushed ipmi-emulator:latest-dev image to docker hub.", "icon_emoji": ":ghost:"}' https://hooks.slack.com/services/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
