# Versioning
## Summary
Given that there are numerous Synse projects each with independent versioning,
it will become difficult to maintain a compatibility matrix. To alleviate this,
Synse projects will adopt a standardized project versioning process.

## High Level Work Items
- Version all projects per this document

## Proposal
In Synse v2 and earlier, all Synse components were versioned independently. This
was generally fine for the time, but as the product matures this will make it
difficult to maintain a matrix of version compatibility between components.

To simplify this, the following patterns will be adopted when it comes to versioning
(/releasing) new versions of Synse components.

* The components' major version should reflect the API version of Synse that it supports,
  e.g. for Synse v3, all components should be rev'ed to `3.x.x`.
  * This means that all components with the same major version should be compatible.
* The components' minor version does not need to match the minor version of any other
  Synse component. It does, however need to be backwards compatible with all previous
  minor versions within the major version.
* The micro version can be bumped as needed and should generally designate small changes.
