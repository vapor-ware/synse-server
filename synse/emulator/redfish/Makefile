
redfish-yml:
	docker-compose -f redfish.yml build
	docker-compose -f redfish.yml up redfish-emulator

build-x64:
	docker build -f Dockerfile.x64 -t vaporio/redfish-emulator-x64 .
