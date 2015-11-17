<img src="http://www.vapor.io/wp-content/uploads/2015/11/openDCRElogo.png" width=144 height=144 align=right>

#OpenDCRE

#Overview
OpenDCRE provides a securable RESTful API for monitoring and control of data center and IT equipment, including reading sensors and server power control - via power line communications (PLC) over a DC bus bar, or via IPMI over LAN.  The OpenDCRE API is easy to integrate into third-party monitoring, management and orchestration providers, while providing a simple, curl-able interface for common and custom devops tasks.

Additional documentation may be found on the <a href="http://wiki.opendcre.com/">Vapor wiki</a>.

#Contents

The OpenDCRE project relies on nginx as its web server, with uwsgi as a reverse proxy to a Python Flask endpoint.  The OpenDCRE uwsgi and nginx configuration files are <b>opendcre_nginx.conf</b>, <b>opendcre_uwsgi.conf</b> and <b>uwsgi.conf</b>.  These files may be edited to suit site-specific needs, change HTTP port, support HTTPS/auth, etc.

The core OpenDCRE Python implementation is distributed as a Python package (<b>opendcre_southbound</b>), and <b>runserver.py</b>, in the OpenDCRE root, is used by uwsgi to launch the Flask implementation.

<b>start_opendcre.sh</b> and <b>start_opendcre_emulator.sh</b> are shell scripts used to start OpenDCRE in hardware (HAT) mode or emulator mode.

To configure the IPMI bridge for OpenDCRE, an example configuration file <b>bmc_config_sample.json</b> is provided, where BMC IP address, username, password and authentication type (NONE, PASSWORD, MD5, MD2) may be chosen.  Copy or move <b>bmc_config_sample.json</b> to <b>bmc_config.json</b> and build and run the OpenDCRE container to have the IPMI BMC settings take effect.

Within the OpenDCRE southbound package, <b>__init__.py</b> contains the main Flask implemementation, which relies on <b>devicebus.py</b> which handles serial communications and command/response framing.  <b>version.py</b> contains the OpenDCRE version - if creating a new/changed version of the API, version numbers must be changed in this file only.

Additionally, the devicebus emulator (<b>devicebus_emulator.py</b>) is part of the OpenDCRE southbound package, and <b>simple.json</b> is used to configure the OpenDCRE emulator (see the OpenMistOS web site for API and emulator configuration reference).

<b>bus-test.py</b> is a simple test harness that runs a suite of tests against the endpoint and emulator.  The <b>tests</b> subdirectory of the OpenDCRE southbound package stores JSON emulator configuration files linked to the test classes.

#Building OpenDCRE as a Docker Container

To build a custom distribution of OpenDCRE (for example, to include site-specific TLS certificates, or to configure nginx to use site-specific authn/authz), the included Dockerfile can be used to package up the distribution.

In the simplest case, from the opendcre directory:

```docker build -t opendcre .```

#Running and Testing OpenDCRE

OpenDCRE expects a volume to be exposed for logs (/logs).  Additionally, OpenDCRE, by default, uses TCP port 5000 to listen for API requests.  In cases where the OpenDCRE HAT is used with the OpenDCRE container, the /dev/ttyAMA0 serial device is also required.

<b>To start OpenDCRE with the HAT device attached:</b>

```docker run -d -p 5000:5000 -v /var/log/opendcre:/logs --device /dev/ttyAMA0:/dev/ttyAMA0 opendcre ./start_opendcre.sh```

<b>To start OpenDCRE in emulator mode:</b>

```docker run -d -p 5000:5000 -v /var/log/opendcre:/logs opendcre ./start_opendcre_emulator.sh```

<b>To run the OpenDCRE test suite:</b>

```docker run -ti -v /var/log/opendcre:/logs opendcre ./opendcre_southbound/bus-test.py```

#License

OpenDCRE is released under GPLv2 - see LICENSE for more information.
