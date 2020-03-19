# Deploying on Kubernetes

This directory contains an example deployment of Synse Server with emulator plugin
for [Kubernetes][kubernetes].

## Setup

For this example you will need:

- a basic understanding of Kubernetes
- an operational Kubernetes cluster
- access to the Kubernetes cluster
- [`kubectl`][kubectl], with the cluster set as the current context

## Usage

Deploying to your cluster should be straightforward using standard `kubectl` commands:

```
kubectl apply -f deployment.yaml
```

You can check to see if the Pod came up and is running. Passing in the `-o wide` flag
will also give the address of the Pod in the cluster.

```console
$ kubectl get pods -o wide
NAME                    READY     STATUS    RESTARTS   AGE       IP           NODE
synse-f6956f758-l7hz2   2/2       Running   0          28s       10.1.0.189   docker-for-desktop
```

You can't query the server endpoint directly without setting up a service, ingress, or some other means of
access. Instead, you can [run a debug container](https://kubernetes.io/docs/tasks/debug-application-cluster/debug-service/#running-commands-in-a-pod)
on the cluster to get on the same network.

```console
$ kubectl run -it --rm --restart=Never alpine --image=alpine sh
If you don't see a command prompt, try pressing enter.
/ #
```

We'll need something like `curl`, which can be installed with

```console
/ # apk add curl
fetch http://dl-cdn.alpinelinux.org/alpine/v3.9/main/x86_64/APKINDEX.tar.gz
fetch http://dl-cdn.alpinelinux.org/alpine/v3.9/community/x86_64/APKINDEX.tar.gz
(1/5) Installing ca-certificates (20190108-r0)
(2/5) Installing nghttp2-libs (1.35.1-r0)
(3/5) Installing libssh2 (1.8.2-r0)
(4/5) Installing libcurl (7.64.0-r1)
(5/5) Installing curl (7.64.0-r1)
Executing busybox-1.29.3-r10.trigger
Executing ca-certificates-20190108-r0.trigger
OK: 7 MiB in 19 packages
```

Now, using the Synse Pod IP from before, the API should be accessible:

```console
/ # curl 10.1.0.189:5000/test
{
  "status":"ok",
  "timestamp":"2019-05-17T13:13:48.412790Z"
}
```

> **Note**: In this example deployment, Synse Server and the emulator plugin are being
> run in the same Pod for simplicity's sake. This works fine as an example use case, but
> it is generally not recommended to run plugins in the same Pod as Synse Server - they
> should really be their own deployment.

[kubernetes]: https://kubernetes.io/
[kubectl]: https://kubernetes.io/docs/tasks/tools/install-kubectl/
