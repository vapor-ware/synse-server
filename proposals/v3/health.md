# Health Checks
## Summary
Not all Synse components currently expose a health check, and the ones that do
only check for "reachable" or "not reachable". In many cases, this is enough, but
having finer-grained detail about the heath of a service may make it easier to
manage and observe.

The notion of a *liveness* and *readiness* probe are present in Kubernetes, so
each Synse component will need to provide this liveness and readiness information.

## High Level Work Items
- Add a means for simple health check for plugins
- Add a section in plugin configuration for health checks
- Update Synse Server's health checks to be based on additional information (e.g. connected to plugins)

## Proposal
### Synse Server
Synse Server had a `/test` endpoint which can be used for basic readiness and liveness
probes. This endpoint does not have any internal checks, so it is just a measure of
whether or not the webserver is running and reachable. In many cases, this is fine.

Additional heath checking behavior can provide finer-grained detail on whether or not
Synse Server is ready and healthy. This may or may not necessarily be useful for a
probe, but at the very least it provides insight into Synse Server's operational state.

Potential points that could constitute a measure of health for Synse Server include:
- Cache readiness (are all of the caches built and okay?)
- Plugin responsiveness (is Synse Server able to reach all of the configured plugins?)
  - A question arises here about partial failures and how that may impact overall health state
 
### Synse Plugins
Synse Plugins (aka. the SDK) do not currently expose any sort of liveness or readiness
state. A plugin should be considered ready when it reaches its main run loop and starts
reading from devices. A plugin should be considered alive when it is actively running and
reading from devices without error (or within some margin of error for device actions).

Using the [example](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-probes/#define-a-liveness-command)
found on the Kubernetes website, the SDK can place a "health" file on the filesystem
which can be read from to determine whether that plugin container is healthy/live.

A configuration option, `healthcheck`, allows:
- health check behavior to be enabled/disabled (optional)
- overriding the path at which the health file is written to (optional)

If no `healthcheck` section is present in the configuration, the default behavior is to
run the plugin with health check enabled and to have the health file placed at 
`/etc/synse/healthy`.

An example configuration with the default values follows:

```yaml
health:
  enabled: true
  path: /etc/sysne/healthy
```

In Kubernetes, this can be configured as a liveness probe with something like:
```yaml
    ...
    livenessProbe:
      exec:
        command:
        - cat
        - /etc/synse/healthy
      initialDelaySeconds: 5
      periodSeconds: 3
```
