The certs directory contains platform specific certs - one for each Docker container to be built. Each cert
has slightly different metadata attached to it, particularly, the 'Common Name' field. For now, that field
is filled in with the container name. See below for metadata assignments for each sub-folder within the certs
directory. Note that a '.' as a value for a field denotes that the field was left blank.

SOUTHBOUND_MACOS
----------------
Country Name (2 letter code):                   US
State or Province Name (full name):             Texas
Locality Name (eg, city):                       Austin
Organization Name (eg, company):                VaporIO
Organizational Unit Name (eg, section):         .
Common Name (e.g. server FQDN or YOUR name):    vaporio/vapor-core-southbound-macos
Email Address:                                  .


SOUTHBOUND_RPI
--------------
Country Name (2 letter code):                   US
State or Province Name (full name):             Texas
Locality Name (eg, city):                       Austin
Organization Name (eg, company):                VaporIO
Organizational Unit Name (eg, section):         .
Common Name (e.g. server FQDN or YOUR name):    vaporio/vapor-core-southbound-rpi
Email Address:                                  .


TEST_CERTS
----------
Country Name (2 letter code):                   US
State or Province Name (full name):             Texas
Locality Name (eg, city):                       Austin
Organization Name (eg, company):                VaporIO
Organizational Unit Name (eg, section):         .
Common Name (e.g. server FQDN or YOUR name):    vapor-core-southbound-test-container
Email Address:                                  .
