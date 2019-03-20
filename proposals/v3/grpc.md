# GRPC API

> **03/20/2019**: [Amendment 2](amendment-2.md) changes have been applied to this document:
>   - `system` field is no longer supported
>   - `systemOfMeasure` field is no longer supported

## Summary
The Synse GRPC API is used to communicate to Synse Plugins. Synse Server uses this
API for all plugin communication, including reading and writing,

Synse v3 brings a number of changes both to how devices are modeled and to information
that Synse exposes to the user via the HTTP API. In order to support all of the changes,
the GRPC API must be updated so that the appropriate data may flow between Synse Server
and the Synse plugins.

## High Level Work Items
- Update the GRPC API according to this document's spec
- Add python client wrapper to GRPC python package

## Proposal
This document outlines the Synse v3 GRPC API. It lists the RPC routes that it will support
and the messages for each RPC route.

### Contents

* [RPC Routes](#rpc-routes)
  * [Devices](#devices)
  * [Health](#health)
  * [Metadata](#metadata)
  * [Read](#read)
  * [Read Cache](#read-cache)
  * [Test](#test)
  * [Transaction](#transaction)
  * [Version](#version)
  * [Write Async](#writeasync) 
  * [Write Sync](#writesync) 
* [Messages](#messages)
  * [Empty](#empty)
  * [v3 Bounds](#v3bounds)
  * [v3 Device](#v3device)
  * [v3 Device Capability](#v3devicecapability)
  * [v3 Device Output](#v3deviceoutput)
  * [v3 Device Selector](#v3deviceselector)
  * [v3 Health](#v3health)
  * [v3 Health Check](#v3healthcheck)
  * [v3 Metadata](#v3metadata)
  * [v3 Output Unit](#v3outputunit)
  * [v3 Reading](#v3reading)
  * [v3 Read Request](#v3readrequest)
  * [v3 Tag](#v3tag)
  * [v3 Test Status](#v3teststatus)
  * [v3 Transaction Selector](#v3transactionselector)
  * [v3 Transaction State](#v3transactionstate)
  * [v3 Version](#v3version)
  * [v3 Write Data](#v3writedata)
  * [v3 Write Capability](#v3writecapability)
  * [v3 Write Payload](#v3writepayload)
  * [v3 Write Transaction](#v3writetransaction)

### RPC Routes

#### Devices
Gets all devices that a plugin manages.

| Message | Link |
| :------ | :--- |
| *Request* | [V3DeviceSelector](#v3deviceselector) |
| *Response* | [V3Device](#v3device) (stream) |


#### Health
Get the health status of a plugin.

| Message | Link |
| :------ | :--- |
| *Request* | [Empty](#empty) |
| *Response* | [V3Health](#v3health) |


#### Metadata
Get the plugin meta-information.

| Message | Link |
| :------ | :--- |
| *Request* | [Empty](#empty) |
| *Response* | [V3Metadata](#v3metadata) |


#### Read
Read from the specified plugin device(s).

| Message | Link |
| :------ | :--- |
| *Request* | [V3ReadRequest](#v3readrequest) |
| *Response* | [V3Reading](#v3reading) (stream) |


#### Read Cache
Get the cached readings from the plugin. If a plugin is not configured
to cache readings, it will return the readings maintained in the current
read state.

| Message | Link |
| :------ | :--- |
| *Request* | [V3Bounds](#v3bounds) |
| *Response* | [V3Reading](#v3reading) (stream) |


#### Test
Check if the plugin is reachable available.

| Message | Link |
| :------ | :--- |
| *Request* | [Empty](#empty) |
| *Response* | [V3TestStatus](#v3teststatus) |


#### Transaction
Get the state and status for the specified write transaction.

| Message | Link |
| :------ | :--- |
| *Request* | [V3TransactionSelector](#v3transactionselector) |
| *Response* | [V3TransactionState](#v3transactionstate) (stream) |


#### Version
Get the version information for the plugin.

| Message | Link |
| :------ | :--- |
| *Request* | [Empty](#empty) |
| *Response* | [V3Version](#v3version) |


#### WriteAsync
Write data to the specified plugin device in an asynchronous request.

| Message | Link |
| :------ | :--- |
| *Request* | [V3WritePayload](#v3writepayload) |
| *Response* | [V3WriteTransaction](#v3writetransaction) |

#### WriteSync
Write data to the specified plugin device in a synchronous request.

| Message | Link |
| :------ | :--- |
| *Request* | [V3WritePayload](#v3writepayload) |
| *Response* | [V3TransactionState](#v3transactionstate) (stream) |


### Messages

#### Empty
An empty message (no fields) which is used for RPC routes which do not require
any input.


#### V3Bounds
Specifies time bounds. Bounds should be given in RFC3339(Nano) format.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *start* | string | RFC3339 timestamp specifying the beginning of the time bound. If left unspecified, the start is unbound. |
| *end* | string | RFC3339 timestamp specifying the ending of the time bound. If left unspecified, the end is unbound. |


#### V3Device
Device metadata. This provides all of the pertinent known data associated with
a device managed by the plugin.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *timestamp* | string | RFC3339 timestamp for when the device info was gathered. |
| *id* | string | The globally unique ID for the device. |
| *type* | string | The type of device. |
| *metadata* | map<string,string> | Any arbitrary metadata associated with the device. |
| *plugin* | string | The name of the plugin that the device is managed by. |
| *info* | string | Additional information for the device. |
| *tags* | repeated [V3tag](#v3tag) | The tags that are associated with the device. |
| *sortIndex* | int32 | A 1-based sort ordinal for the device. This will help determine where the device shows up in the scan. |
| *capabilities* | [V3DeviceCapability](#v3devicecapability) | The read/write capabilities of the device. |
| *output* | repeated [V3Output](#v3deviceoutput) | The reading outputs that the device can generate on read. |


#### V3DeviceCapability
Specifies the capabilities that a device exposes via Synse.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *mode* | string | The capability mode of the device ("r" *(read only)*, "w" *(write only)*, "rw" *(read-write)*). |
| *write* | [V3WriteCapability](#v3writecapability) | The write capabilities of the device. |


#### V3DeviceOutput
Specifies the output types for a device's readings.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *name* | string | The name of the device output. This can be namespaced. |
| *type* | string | The type of the output. This is the last element of the namespaced output name. |
| *precision* | int | The decimal precision of the output. A precision of 0 (default) means no precision is applied. |
| *scalingFactor* | double | The factor to multiply the reading result returned from the device. This can be positive, negative, whole, or decimal. |
| *unit* | [V3OutputUnit](#v3outputunit) | The unit of measure for the reading output. |


#### V3DeviceSelector
A selector for choosing devices for various operations.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *tags* | repeated [V3Tag](#v3tag) | A collection of all the tags to be used as selectors. |
| *id* | string | The ID of the device. If this is set, tags will be ignored. |


#### V3Health
Health status for the plugin.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *timestamp* | string | RFC3339 timestamp of the time when the health was checked. |
| *status* | enum HealthStatus | The overall status (one of: unknown, ok, failing). |
| *checks* | repeated [V3HealthCheck](#v3healthcheck) | All of the health checks which make up the overall health of a plugin. |


#### V3HealthCheck
Health check status for a plugin.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *name* | string | The name of the health check. |
| *status* | enum HealthStatus | The status of the health check. |
| *message* | string | Any additional information associated with the health check. |
| *timestamp* | string | RFC3339 timestamp at which the check was last completed. |
| *type* | string | The type of health check. The different kinds of health check are defined in the SDK. |


#### V3Metadata
Plugin metadata. This information static information about the plugin.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *name* | string | The name of the plugin. |
| *maintainer* | string | The maintainer of the plugin. |
| *tag* | string | The normalized tag for the plugin metainfo. |
| *description* | string | A brief description of the plugin. |
| *vcs* | string | A link to the plugin's VCS repo. |


#### V3OutputUnit
The unit of measure for a [v3 Device Output](#v3deviceoutput).

| Field | Type | Description |
| :---- | :--- | :---------- |
| *name* | string | The full name of the unit, e.g. "degrees celsius". |
| *symbol* | string | The symbolic representation of the unit, e.g. "C". |


#### V3Reading
A reading response from a device.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *id* | string | The ID of the device being read from. |
| *timestamp* | string | RFC3339 timestamp for when the reading was taken. |
| *type* | string | The type of the reading. |
| *deviceType* | string | The type of the device, as specified by the plugin. |
| *context* | map<string,string> | Any additional info associated with the reading. |
| *unit* | [V3OutputUnit](#v3outputunit) | The unit of measure for the reading. |
| *value* | * | The value of the reading. |


#### V3ReadRequest
A request for device readings.

| Field | Type | Description |
| :---- | :--- | :---------- |
| selector | [V3DeviceSelector](#v3deviceselector) | The selector for the device(s) to read from. |


#### V3Tag
Specification for a single [tag](tags.md).

| Field | Type | Description |
| :---- | :--- | :---------- |
| *namespace* | string | The namespace for the tag. |
| *annotation* | string | The annotation for the tag. |
| *label* | string | The tag label. |


#### V3TestStatus
Plugin status response for reachability and availability.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *ok* | bool | A flag that describes whether the plugin is reachable or not. |


#### V3TransactionSelector
Identifying information for a write transaction.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *id* | string | The ID of a transaction. |


#### V3TransactionState
The state and status for a write transaction.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *id* | string | The ID of the write transaction. |
| *created* | string | RFC3339 timestamp of when the transaction was created. |
| *updated* | string | RFC3339 timestamp of when the transaction was last updated. |
| *status* | enum WriteStatus | The status of the write (unknown, pending, writing, done). |
| *state* | enum WriteState | The state of the write (ok, error).  |
| *message* | string | Context information for the asynchronous write when there is an error. |
| *context* | [V3WriteData](#v3writedata) | The data that was written for the write transaction. |
| *timeout* | string | The timeout within which the transaction remains valid. |


#### V3Version
Version information for a plugin.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *pluginVersion* | string | The semantic version of the plugin. |
| *sdkVersion* | string | The version of the SDK that the plugin uses. |
| *buildDate* | string | The timestamp from when the plugin was built. |
| *gitCommit* | string | The commit hash at which the plugin was built. |
| *gitTag* | string | The tag name at which the plugin was built. |
| *arch* | string | The architecture that the plugin was built for. |
| *os* | string | The operating system that the plugin was built for. |


#### V3WriteCapability
The write capabilities for a device.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *actions* | repeated string | The actions that the device supports when writing. |


#### V3WriteData
The data to write to a device.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *action* | string | The action string for the write. |
| *data* | bytes | The action data for the write. |


#### V3WritePayload
The selector for the device write, as well as the data to write to that device.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *selector* | [V3DeviceSelector](#v3deviceselector) | The selector for the device to write to. This should resolve to a single device. |
| *data* | repeated [V3WriteData](#v3writedata) | The data to write to the device. |


#### V3WriteTransaction
Information associating a write action with a transaction for asynchronous tracking.

| Field | Type | Description |
| :---- | :--- | :---------- |
| *context* | [V3WriteData](#v3writedata) | The data that was written for the write transaction. |
| *id* | string | The ID of the write transaction. |
| *device* | string | The ID of the device written to. |
| *timeout* | string | The timeout within which the transaction remains valid. |
