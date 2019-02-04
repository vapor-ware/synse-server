# Monitoring & Metrics
## Summary
Adding support for metrics export on Synse services grants additional observability
into how the system is operating. Having metrics for service performance, bandwidth,
latency, etc. will allow us to more easily identify trouble points and could lend to
mitigation of issues before they become issues. 

## High Level Work Items
- Add configuration to Synse Server for metrics export
- Define and collect a set of metrics for Synse Server to export
- Add configuration to Synse SDK for metrics export
- Define and collect a set of metrics for Synse SDK to export
- Determine the means by which plugins will export their metrics

## Proposal
For both Synse Server and Synse Plugins (aka. the Plugin SDK), we will support the
collection and export of metrics for Prometheus.

This proposal is only to support metrics export by services; it makes no attempt
to describe how metrics are collected, stored, and analyzed from these services.

### Synse Server
Synse Server will export its collected metrics via its HTTP API at the versionless
`/metrics` endpoint.

The metrics that will be collected need to be determined, but should generally be
pretty standard:
- requests/sec
- request latency
- errors/sec
- memory used
- ...

A configuration section will be added to enable or disable metrics collection.
By default, it will be disabled. An example of the new config section follows:

```yaml
metrics:
  enabled: false
```

### Synse Plugins
The plugins will expose similar metrics as does Synse Server, however their metrics
originate from the GRPC API. It is unclear which metrics, if any, should be gathered
from device actions (read/write).

Unlike Synse Server, Synse Plugins do not expose an HTTP API, so the means by which
the metrics are exported must be researched and determined. It is possible that they
could be exported via the GRPC API. A lightweight HTTP server may need to be set up
to export metrics, though the actual implementation details are unknown at this time.

The metrics that will be collected need to be determined, but should generally be
pretty standard:
- requests/sec
- request latency
- errors/sec
- memory used
- ...

A configuration section will be added to enable or disable metrics collection.
By default, it will be disabled. An example of the new config section follows:

```yaml
metrics:
  enabled: false
```