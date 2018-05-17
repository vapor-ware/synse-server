# Deploying on Kubernetes
This directory contains an example deployment of Synse Server with a containerized
Emulator Plugin for [Kubernetes][kubernetes].

## Deployments
As a general note - the Emulator Plugin does not need to be containerized. In
fact, it is built into non-slim Synse Server 2.0+ images so that it can run
alongside Synse Server, providing an easy way to get started/demo/play with it.

In this case, we use a containerized version of the same emulator in order to
give us a plugin that is not dependent on any platform or hardware. This makes 
the example here a good place to get started. Additionally, we use a slim version
of Synse Server as to prove that the data is coming from the external emulator only.

The example deployment here sets up a simple Synse Server instance and an instance
of the Plugin Emulator within the same pod. Both Synse Server and the plugin are
configured to communicate via gRPC over TCP. Currently, the [plugin SDK][synse-sdk]
(via the [internal gRPC API][synse-grpc]) supports communication via TCP and UNIX
socket, but for Kubernetes deployments, it is highly preferred to use TCP over UNIX
sockets.

## Setup
For this example you will need:
- a basic understanding of Kubernetes
- an operational Kubernetes cluster
- access to the Kubernetes cluster
- [`kubectl`][kubectl], configured to talk to your cluster

It is also recommended that you have a basic understanding of how Synse Server
works, how Synse Plugins work, and how the two interact. This is not required
to get the deployment working, but is useful in understanding the deployment configuration.
For more, see:
- [Synse Server User Guide][synse-user-guide]
- [Synse SDK Documentation][synse-sdk-docs]


## Usage
Deploying to your cluster should be straightforward using standard `kubectl` commands.

With this repo checked out, you can do this locally, e.g.
```
kubectl apply -f synse-with-emulator.yml
```

Or, you can just use the URL to the YAML config
```
kubectl apply -f https://raw.githubusercontent.com/vapor-ware/synse-server/master/deploy/k8s/synse-with-emulator.yml
```

Kubernetes should now do all the heavy lifting!


Once one of the deployments is running, you can test out that Synse Server is reachable.
First you will need to get the IP of pod. From within the cluster:
```console
$ kubectl get pods -o wide
NAME                            READY     STATUS    RESTARTS   AGE       IP             NODE
synse-server-7785ffdd54-dtn98   2/2       Running   0          44s       10.244.0.239   vec8
```

Here, our pod IP is `10.244.0.239`.


Using that IP, we can test that Synse Server is reachable and OK.
```
curl <pod id>:5000/synse/test
```

If successful, you are ready to go. Next, perform a scan to see everything that is available
via the plugin:
```
curl <pod ip>:5000/synse/2.0/scan
```

This should give back a set of devices - in particular:
- 2 LED devices
- 2 temperature devices

If you look at the log output of the Emulator Plugin , you should see that these results
match up with what that plugin had registered on startup.

[kubernetes]: https://kubernetes.io/
[kubectl]: https://kubernetes.io/docs/tasks/tools/install-kubectl/
[synse-sdk]: https://github.com/vapor-ware/synse-sdk
[synse-grpc]: https://github.com/vapor-ware/synse-server-grpc
[synse-user-guide]: http://synse-server.readthedocs.io/en/latest/
[synse-sdk-docs]: http://synse-sdk.readthedocs.io/en/latest/
