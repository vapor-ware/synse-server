# Synse CLI
## Summary
The Synse CLI will need a number of updates in order to work with Synse v3.
In addition to the required updates, additional features can be added, such
as plugin templating. This can make it easier for external/new contributors
to get started with Synse and creating their own plugins. 

## High Level Work Items
- Update to use the [Synse Golang client](api-clients.md); this will provide the
updated v3 interface.
- Redesign CLI internals to:
  - simplify development/usage
  - make it easier to maintain API backwards compatibility
- Add functionality for plugin templating

## Proposal
### API Client Update
Synse CLI currently has its own implementation of a Synse client. In v3, this will
be replaced with an official golang client which all golang projects will use to
interface with Synse Server. 

### Backwards Compatibility
Making the CLI backwards compatible with older versions of Synse Server (e.g. v2)
is not a priority for the initial release of v3. Since v2 is not widely used or
deployed at the moment, this work is secondary to other work items.

The CLI should be redesigned and updated to make it easier to add backwards compatibility
support, however. This will make it easier to add in v2 support as well as any future
backwards compatibility support.

### New Functionality: Plugin Templating
Adding capabilities for simple but robust plugin templating can make authoring
a new plugin much easier. This could be useful in fostering an open source
community with additional plugin contributions. The ultimate goal of this new
functionality would be to auto-generate as much of the boilerplate plugin code
and project structure as possible so the developer can spend more time on the
protocol integration and not have to worry as much about how the plugin is set up.

Below is a non-exhaustive list of the capabilities that this functionality should
have:

- uses YAML configuration to bootstrap plugin
- auto-generates the entrypoint (`main.go`) for the plugin
- auto-generates the plugin metadata
- auto-generates boilerplate for any specified:
   - device handlers
   - output types
   - ...
- auto-generates the package structure for a plugin
- auto-generates plugin setup function (based on any known values)
   - e.g. registering handlers, registering types, etc
- auto-generates plugin config policies
- auto-generatings basic project files
   - dockerignore
   - docker file
   - makefile
   - readme
   - plugin config
