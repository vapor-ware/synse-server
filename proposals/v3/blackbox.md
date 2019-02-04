# Blackbox
## Summary
Blackbox will need to be updated to use the Synse v3 API. The internal modeling
for devices and readings in Blackbox will need to be updated to conform with the
modeling required by the new [tag based routing system](tags.md).

## High Level Work Items
- Update to use the [Synse Golang client](api-clients.md); this will provide the
updated v3 interface.
- Update internal modeling to replace `rack/board/device` info with tags

## Proposal
There is no additional proposal. The work for Blackbox is just a requirement
of the underlying API change.
