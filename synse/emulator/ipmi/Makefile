
# Include common functionality for docker cleanup.
include ../../../../../vapor_common/make_docker_common

ipmi-yml:
	docker-compose -f ipmi.yml build
	docker-compose -f ipmi.yml up ipmi-emulator


build-x64:
	docker build -f Dockerfile.x64 -t vaporio/ipmi-emulator-x64 .
