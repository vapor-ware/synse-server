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
kubectl apply -f .
```

You can check to see if the Pod came up and is running. Passing in the `-o wide` flag
will also give the address of the Pod in the cluster.

```console
$ kubectl get pods -o wide
NAME                            READY     STATUS    RESTARTS   AGE       IP           NODE
synse-server-f6956f758-l7hz2    1/1       Running   0          28s       10.1.0.189   docker-for-desktop
emulator-86df9dcb9c-wpcfd       1/1       Running   0          28s       10.1.0.190   docker-for-desktop
```

You can query the Synse endpoints by setting up port-forwarding to the pod.

```console
kubectl port-forward synse-server-f6956f758-l7hz2 5000:5000
Forwarding from 127.0.0.1:5000 -> 5000
Forwarding from [::1]:5000 -> 5000

```

Now, the API should be accessible from localhost:

```console
/ # curl localhost:5000/test
{
  "status":"ok",
  "timestamp":"2019-05-17T13:13:48.412790Z"
}
```


[kubernetes]: https://kubernetes.io/
[kubectl]: https://kubernetes.io/docs/tasks/tools/install-kubectl/
