# Security
## Summary
Security is a broad and important component of any deployment. With Synse platform's microservice
architecture, minimal security has been previously built in. The assumption has been that
if additional security is needed (e.g. TLS encryption), a service like Nginx could be put
in from of Synse to do TLS termination.

For Synse v3, there are no clear requirements for security features, but there are a number
of open questions which require research and discussion which should inform which security
features, if any, will be needed in v3.

## High Level Work Items
- Enumerate the open questions surrounding security in the Synse platform
- Research and discuss each of the questions and determine which, if any, should be implemented.

## Proposal
Identify the security requirements for the Synse platform and determine how those requirements
should be met. The result of this could be that no changes need to be made to Synse and all
security is done externally (e.g. via sidecar containers).

Below are some topics that should be considered. The topics listed below are not exhaustive.

- **TLS**: Enabling encrypted communication with Synse Server and the Synse Plugins
- **Role Based Access**: Only allow access to devices (r/w) if the user has the required role (related: [Third Party Access](third-party.md))
