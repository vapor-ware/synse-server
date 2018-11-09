# API Clients
## Summary
Existing API clients will need to be updated for Synse v3. 

## High Level Work Items
- Update the API client libraries for the Synse HTTP API
  - python: (https://github.com/vapor-ware/synse-client-python)
  - golang: (https://github.com/vapor-ware/synse-client-go)
- Update the API client libraries for the [Blackbox](blackbox.md) HTTP API
  - python: (https://github.com/vapor-ware/blackbox-client-python)

## Proposal
The existing API clients need to be updated to comply with the Synse v3 [HTTP API spec](api.md).
These clients are either actively used in other projects or will be actively used.

There may be work items for these clients which fall out of discussions on
[third party access](third-party.md).

Support for WebSockets as the transport layer will be added to [Synse Server](server.md#websocket-support),
so API clients will need to be able to support both HTTP and WebSocket transport.