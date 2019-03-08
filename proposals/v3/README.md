# Synse v3 Proposals
This directory contains proposals and specifications for Synse v3. 

## Overview
Synse v3 is the next iteration of the Synse platform that will bring simplifications
and generalizations to the platform, doing away with design patterns from older versions
that are no longer needed. These changes should make the HTTP API more intuitive, make
plugin development simpler, expand the platform's capabilities, and allow for better
visibility and monitoring of the services themselves.

The documents in this directory focus on particular aspects of Synse v3 -- all of
them together are considered the proposal/spec for Synse v3.

### Primary Goals
- Replace the *rack/board/device* routing hierarchy with a tag-based routing system
- Maintain having deterministic device IDs with the IDs being globally unique (instead of only
  being unique to the rack/board)
- Expand API capabilities
- Provide better support for container management/monitoring
- Improve performance, where possible
- Maintain high test coverage

## Table of Contents
0. **[Device Tags](tags.md)** - tag-based routing for Synse devices
0. **[Device IDs](ids.md)** - globally unique device ID generation
0. **[API](api.md)** - the Synse v3 HTTP API
0. **[Reads](reads.md)** - updates to device read behavior in Synse
0. **[Writes](writes.md)** - updates to device write behavior in Synse
0. **[Health Check](health.md)** - implementing service health checks
0. **[Synse Server](server.md)** - general updates and changes to Synse Server 
0. **[Synse SDK](sdk.md)** - general updates and changes to Synse SDK 
0. **[Synse CLI](cli.md)** - updates and new features for the Synse CLI
0. **[GRPC API](grpc.md)** - updates to the GRPC API for communicating with plugins
0. **[Monitoring & Metrics](monitoring.md)** - exposing Synse server metrics
0. **[Third Party Usage](third-party.md)** - goals and requirements for direct third party usage
0. **[Security](security.md)** - updates and enhancements to security capabilities
0. **[Scaffolding](scaffolding.md)** - project tooling and scaffolding
0. **[Tests](tests.md)** - updates to Synse tests and testing methodologies
0. **[API Clients](api-clients.md)** - updates to the various Synse HTTP API clients
0. **[Blackbox](blackbox.md)** - updates to the internal Blackbox project
0. **[Versioning](versioning.md)** - project versioning and component comaptibility

## Appendix
0. [Appendix A](appendix-a.md): Configuration Examples
0. [Appendix B](appendix-b.md): SDK changes

## Amendments
0. [Amendment 1](amendment-1.md): Device FQDN & Aliases 