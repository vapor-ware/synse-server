
snmp-yml:
	docker-compose -f snmp.yml build
	docker-compose -f snmp.yml up snmp-emulator


build-x64:
	docker build -f Dockerfile.x64 -t vaporio/snmp-emulator-x64 .
