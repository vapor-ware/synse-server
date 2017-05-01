# Include common functionality for docker cleanup.
include ../../../../../vapor_common/make_docker_common

snmp-yml:
	docker-compose -f snmp.yml build
	docker-compose -f snmp.yml up snmp-emulator


build-x64:
	docker build -f Dockerfile.x64 -t vaporio/snmp-emulator-x64 .


# get date for tagging on push
date := $(shell /bin/date "+%m%d%y-%H%M")

push-latest-x64:
	docker build -f Dockerfile.x64 -t vaporio/snmp-emulator-x64:$(date) .
	docker tag vaporio/snmp-emulator-x64:$(date) vaporio/snmp-emulator-x64:latest
	docker push vaporio/snmp-emulator-x64:$(date)
	docker push vaporio/snmp-emulator-x64:latest
	curl -X POST --data-urlencode 'payload={"channel": "#checkins", "username": "docker-hub", "text": "Pushed snmp-emulator:latest image to docker hub.", "icon_emoji": ":ghost:"}' https://hooks.slack.com/services/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


push-private-x64:
	docker build -f Dockerfile.x64 -t vaporio/snmp-emulator-x64:$(date) .
	docker tag vaporio/snmp-emulator-x64:$(date) vaporio/snmp-emulator-x64:latest-dev
	docker push vaporio/snmp-emulator-x64:$(date)
	docker push vaporio/snmp-emulator-x64:latest-dev
	curl -X POST --data-urlencode 'payload={"channel": "#checkins", "username": "docker-hub", "text": "Pushed snmp-emulator:latest-dev image to docker hub.", "icon_emoji": ":ghost:"}' https://hooks.slack.com/services/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
