# Include common functionality for docker cleanup.
include ../../../../../vapor_common/make_docker_common

snmp-yml:
	docker-compose -f snmp.yml build
	docker-compose -f snmp.yml up snmp-emulator


build-x64:
	docker build -f Dockerfile.x64 -t vaporio/snmp-emulator-x64 .
