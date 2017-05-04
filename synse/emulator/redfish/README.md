#How to run the Emulator
The emulator can be run outside of a docker container by running the rf-emulator.py program.
To run the emulator within a docker container, navigate to the redfish emulator directory and run
```
make build-x64
```
will build the container, to start the emulator run
```
docker run -p 5040:5040 vaporio/redfish-emulator-x64.
```

##Description
###
* A python 2.7 program
* Uses Flask to serve up Redfish mockup files for GET, PATCH, PUT, POST, DELETE requests
* Creates a database dictionary from specified files in Resource directory, requests access resources in database so no changes are made to original mockup files
* Creates a users dictionary from Accounts schema found in mockup files provided for basic authentication
* Supports HTTP basic authentication and Redfish session token authentication
* For basic auth, client sends auth value in request with user: root and password: redfish
* For token auth, client sends header value in request, 123456789authtoken
* Resource directory contains mockup files for a Rackmount server with Redfish implemented, this mockup comes from DMTF example mockups.
* Emulator default configurations are:
    * Host: 0.0.0.0
    * Port: 5040
    * Redfish version: v1
    * Mockup used: RackmountServerMockUp

##Adding new mockup files
To add new mockup files to be used in the emulator, all mockup files should be placed in the Resources directory.
Mockup files should follow this hierarchy: Resources/<mockup_name>/redfish/v1/…
* Example: Resources/RackmountServerMockUp/redfish/v1

##Usages
* Emulates GET, PUT, PATCH, POST, DELETE requests of a real Redfish service(sortof)
* All resources support GET. Root and version resources do not need authentication to GET. All other resources require authentication via basic auth or token to GET.
Emulates System reset action, client sends a POST requests to:
    /redfish/v1/Systems/<system_name>/Actions/ComputerSystem.Reset
with the payload:
```
json={‘ResetType’: ‘<reset_type>’}
```
Emulates Session registration without authentication, client sends POST request to:
	/redfish/v1/SessionService/Sessions
With the payload:
```
json={"UserName": <username>,
      "Password": <password>}
```
Response from emulator will include path to newly created Session resource, and the auth token for the session. This auth token will not timeout.

##Testing the emulator
Redfish emulator tests lives in synse/tests/redfish_emulator. To run the test, navigate to synse/tests and run
```
make test-redfish-emulator-x64.
```

##Limitations
* HTTPS not implemented
* Relies on static mockup files which may not exactly be a real implementation of a Redfish service
* Basic authentication supports default user: root and password: redfish combination and user and password combinations specified in mockup’s Accounts schema
* Token authentication not true to name, supports one token: 123456789authtoken, and sessions do not timeout.
* Does not support the creation of new computer systems
* Event subscription not implemented
