====================
Configuring OpenDCRE
====================

Customization
--------------

OpenDCRE may be customized in a variety of ways, most commonly by changing the HTTP endpoint port, adding TLS certificates for HTTPS support, or by integrating OpenDCRE with a site-specific authentication provider.

Port
----

To change the port OpenDCRE listens on, edit the ``opendcre_nginx.conf`` file, and rebuild the OpenDCRE docker container.  Be sure to also update the ``DOCKER_RUN`` variable in the  ``/etc/init.d/opendcre`` init.d script to indicate the correct port mapping for the Docker container, as well.
::

    server {
        listen 5000;
        server_name localhost;
        charset utf-8;
        access_log /logs/opendcre.net_access.log;
        error_log /logs/opendcre.net_error.log;
    
        location / {
            add_header 'Access-Control-Allow-Origin' '*';
            uwsgi_pass unix://var/uwsgi/opendcre.sock;
            include /etc/nginx/uwsgi_params;
        }
    } 

TLS/SSL
-------

TLS/SSL certificates may be added to OpenDCRE via Nginx configuration.  Refer to Nginx documentation for instructions on how to enable TLS.

Authentication
--------------

As OpenDCRE uses Nginx as its reverse proxy, authentication may be enabled via Nginx configuration - see Nginx documentation for instructions on how to enable authentication.