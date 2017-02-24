
.. _opendcre-configuration:

====================
Configuring OpenDCRE
====================

OpenDCRE may be customized in a variety of ways, most commonly through the OpenDCRE configuration file, but
also through supporting configurations (e.g. Nginx configurations).

.. _opendcre-configuration-options:

Configuration Options
---------------------

OpenDCRE configurations are made up of two files -- default configurations, and override configurations. As the name
suggests, the default configurations are what come pre-built into OpenDCRE and what OpenDCRE will fall back to if no
override is specified. The default configurations can be found at ``/opendcre/default/default.json`` in the OpenDCRE
container.

.. code-block:: json

    {
      "scan_cache_file": "/tmp/opendcre/cache.json",
      "cache_timeout": 600,
      "cache_threshold": 500,

      "devices": {
        "ipmi": {
          "from_config": "bmc_config.json"
        }
      }
    }


The override configurations are user-specified at run time. These configurations can be mounted into the container
as a volume at ``/opendcre/override/config.json``. The configuration override file can be any JSON file with
"config" in the filename. Of course, configurations do not need to be volume-mounted into the container, though it is
convenient in various situations. In cases where it is easier to just replace the default configuration altogether,
do so and rebuild the OpenDCRE docker image (see :ref:`opendcre-build-from-source`).

As an example, if we wanted to override the *cache_timeout* configuration, we could mount in ``config.json`` which
contains:

.. code-block:: json

    {
      "cache_timeout": 1000
    }

In this case, the default values will be used for everything but *cache_timeout*.

Below are descriptions for each of the supported configuration file fields.

:scan_cache_file:
    The path and filename of the file used to cache OpenDCRE data, such as board records used by the
    "scan" command. The default value of "/tmp/opendcre/cache.json" typically is suitable and does not need to be
    changed.

:cache_timeout:
    The scan cache's time-to-live, in seconds, after which cache records will be invalidated.

:cache_threshold:
    The maximum number of entries to store in the scan cache.

:devices:
    The devices parameter is used to describe the various bus types and devices available to OpenDCRE. It
    accepts keys of "plc" (:ref:`opendcre-plc-device`), "ipmi" (:ref:`opendcre-ipmi-device`), and "redfish"
    (:ref:`opendcre-redfish-device`), though none are required. See the linked sections for each devicebus type
    for examples of the configuration for each.

Continuing with the example above, we can see how actual devices are configured within the referenced IPMI config file,
``bmc_config.json``:

.. code-block:: json

    {
      "racks": [
        {
          "rack_id": "rack_1",
          "bmcs": [
            {
              "bmc_ip": "192.168.1.110",
              "username": "ADMIN",
              "password": "ADMIN"
            },
            {
              "bmc_ip": "192.168.1.111",
              "bmc_port": 622,
              "username": "ADMIN",
              "password": "ADMIN",
              "hostnames": ["atom"],
              "ip_addresses": ["192.169.1.111"]
            }
          ]
        }
      ]
    }

Here, we are configuring two BMCs, both on a single rack -- "rack_1". The first BMC is at IP 192.168.1.110 with
username ADMIN and password ADMIN. No port is specified, so it uses the default port of 623. The second BMC is at
IP 192.168.1.111 with username ADMIN and password ADMIN. It has a non-standard port specified which will be used
to communicate with that BMC.

See the :ref:`opendcre-ipmi-device` section for greater detail on these configuration options.


Port
----

By default, OpenDCRE listens on port 5000. To change the port OpenDCRE listens on, edit the ``opendcre_nginx.conf`` file,
and the port exposed in the Dockerfile, then rebuild the OpenDCRE docker image (see :ref:`opendcre-build-from-source`).
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

TLS/SSL certificates may be added to OpenDCRE via Nginx configuration. Refer to the
`Nginx documentation <https://nginx.org/en/docs/>`_ for instructions on how to enable TLS.


Authentication
--------------

As OpenDCRE uses Nginx as its reverse proxy, authentication may be enabled via Nginx configuration --
see the `Nginx documentation <https://nginx.org/en/docs/>`_ for instructions on how to enable authentication.
