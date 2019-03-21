# Amendment 2: Removing server side support for unit conversions
> **Amendment Date**: 03/20/2019

## Summary
The original Synse v3 proposal laid out a system for unit conversions based on System
of Measure (SoM) (e.g., imperial, metric), where the default SoM would be metric. The
gRPC API, WebSocket API, and HTTP API exposed a means by which the consumer could choose
which SoM they wanted, e.g. `/read/12592352?som=imperial`.

Per this amendment, this functionality is dropped in favor of all unit conversions
happening on the front end (e.g. the consumer of the Synse data).

All plugin readings should be surfaced as their metric values. It is up to the plugin to
ensure that any raw sensor data is appropriately converted. If a sensor returns data as
imperial (or any other measure), it should convert those data to metric internally.


## Implications
This change affects a number of areas in the Synse v3 spec:

- SDK
  - Unit conversion is not supported on OutputTypes.
  - OutputTypes are vastly simplified because of this and are effectively just
    metadata (name, precision, unit). This is largely the same information that
    was associated with OutputTypes in v2.
- gRPC
  - `som` is no longer supported as a parameter.
- Synse Server
  - HTTP API no longer supports `som` as a parameter.
  - WebSocket API no longer supports `som` as a parameter.
  
There are some related but non-affected areas of the Synse v3 spec:

- SDK
  - OutputType simplification will still occur.
  - OutputTypes will still not be required in the configuration.
  - A collection of built-in OutputTypes will still be included in the SDK.
  

## Changed Sections
For all of the above, the corresponding sections of the v3 spec have been updated and a
reference to this page has been included.

- [HTTP API](api.md)
- [WebSocket API](api-websocket.md)
- [gRPC API](grpc.md)
- [SDK](sdk.md)