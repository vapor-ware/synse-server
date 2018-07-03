.. _advancedUsage:

Advanced Usage
==============
This section covers some of the more advanced features, components, and usage
of Synse Server.

Health Check / Liveness Probe
-----------------------------

When creating a :ref:`deployment` with Docker Compose, Kubernetes, etc., you can set a
"health check" (or liveness and readiness probe) for the service. While you can define
your own, Synse Server comes with one build in at ``bin/ok.sh``. This will check that the
*/test* endpoint is reachable and returning a 200 status with 'ok' in the JSON status response.

To illustrate, below is a simple compose file to run a Synse Server instance (with no plugins
configured, for simplicity of the example)

.. code-block:: yaml

    version: "3.4"
    services:
      synse-server:
        container_name: synse-server
        image: vaporio/synse-server:latest
        ports:
          - 5000:5000
        healthcheck:
          test: ["CMD", "bin/ok.sh"]
          interval: 1m
          timeout: 5s
          retries: 3
          start_period: 5s

.. note::

    The ``healthcheck`` option is supported in compose file versions 2.1+, but the
    ``start_period`` option is only supported in compose file versions 3.4+. For more,
    see the `healthcheck reference <https://docs.docker.com/compose/compose-file/#healthcheck>`_.


This can be run with ``docker-compose -f compose.yml up -d``. Then, checking the state, you should see
something similar to

.. code-block:: console

    $ docker ps
    CONTAINER ID        IMAGE                  COMMAND             CREATED              STATUS                        PORTS                    NAMES
    4dd14ab5b25a        vaporio/synse-server   "bin/synse.sh"      About a minute ago   Up About a minute (healthy)   0.0.0.0:5000->5000/tcp   synse-server

*Note the (healthy) state specified under the STATUS output.*

You can use ``docker inspect <container>`` to get more details on the health check. This is
especially useful if the health check is failing or stuck.

.. _psdKubernetes:

Plugin Service Discovery (via Kubernetes)
-----------------------------------------
If deploying Synse Server with Kubernetes, configuring plugins manually (either via config
file or environment variable) can quickly become cumbersome, especially if the plugin
`Pod <https://kubernetes.io/docs/concepts/workloads/pods/pod/>`_ is restarted or scheduled
on a different Node. To make this easier, Synse Server supports Plugin service discovery
leveraging the Kubernetes API.

Currently, service discovery is only supported via
`Kubernetes Service Endpoints <https://kubernetes.io/docs/concepts/services-networking/service/>`_
using label matching. Below is an example Kubernetes configuration that will create a Service and
Deployment for Synse Server and the Emulator Plugin. Synse Server is configured to discover the
plugin using endpoint labels, specifically the ``app=synse`` and ``component=plugin`` labels.

.. code-block:: yaml

    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: server-config
      labels:
        name: server-config
    data:
      config.yml: |
        logging: debug
        plugin:
          discover:
            kubernetes:
              endpoints:
                labels:
                  app: synse
                  component: plugin
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: synse
      labels:
        app: synse
        component: server
    spec:
      ports:
        - port: 5000
          name: http
      clusterIP: None
      selector:
        app: synse
        component: server
    ---
    apiVersion: extensions/v1beta1
    kind: Deployment
    metadata:
      name: synse
      labels:
        app: synse
        component: server
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: synse
          component: server
      template:
        metadata:
          labels:
            app: synse
            component: server
        spec:
          volumes:
            - name: server-config
              configMap:
                name: server-config
          containers:
            - name: synse-server
              image: vaporio/synse-server:latest
              imagePullPolicy: Never
              ports:
                - name: http
                  containerPort: 5000
              volumeMounts:
                - name: server-config
                  mountPath: /synse/config
    ---
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: emulator-config
      labels:
        name: emulator-config
    data:
      config.yml: |
        version: 1.0
        debug: true
        network:
          type: tcp
          address: ":5001"
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: emulator-plugin
      labels:
        app: synse
        component: plugin
        plugin: emulator
    spec:
      ports:
        - port: 5001
          name: http
      clusterIP: None
      selector:
        app: synse
        component: plugin
        plugin: emulator
    ---
    apiVersion: extensions/v1beta1
    kind: Deployment
    metadata:
      name: emulator-plugin
      labels:
        app: synse
        component: plugin
        plugin: emulator
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: synse
          component: plugin
          plugin: emulator
      template:
        metadata:
          labels:
            app: synse
            component: plugin
            plugin: emulator
        spec:
          volumes:
            - name: emulator-config
              configMap:
                name: emulator-config
          containers:
            - name: emulator
              image: vaporio/emulator-plugin:latest
              imagePullPolicy: Never
              ports:
                - name: http
                  containerPort: 5001
              env:
                - name: PLUGIN_CONFIG
                  value: /tmp/config
              volumeMounts:
                - name: emulator-config
                  mountPath: /tmp/config
