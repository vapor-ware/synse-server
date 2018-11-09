# Plugin Templating
## Summary
To facilitate community contributions to the Synse platform in the form of
additional plugin support, a plugin templating tool will be created. This tool
will be used to bootstrap new plugin projects (and could potentially be applied
to existing ones retroactively for consistency in plugin structure). The ultimate
goal of this tool is to do most of the heavy-lifting on the boilerplate plugin code
and provide a user-friendly interface for it, so the plugin implementor can spend
more time focusing on the device interactions rather than figuring out hwo to set up
the plugin correctly.

## High Level Work Items
- Design capabilities and workflow for templating tool
- Create the new plugin template tool, including tests

## Proposal
The plugin templating tool will be a CLI which can generate the basic project structure
for a plugin and fill in boilerplate plugin code as well. It should be able to take
user input from the command line, or to use a YAML configuration file. Below are some
of the capabilities that it should have.

- auto-generate the entrypoint (`main.go`) for the plugin
- auto-generate the plugin metadata
- auto-generate boilerplate for any specified:
   - device handlers
   - output types
   - ...
- auto-generate the package structure for a plugin
- auto-generate plugin setup function (based on any known values)
   - e.g. registering handlers, registering types, etc
- auto-generate plugin config policies
- auto-generating basic project files
   - dockerignore
   - docker file
   - makefile
   - readme
   - plugin config
   

This tool is not required for the Synse v3 release, but is recommended as it strengthens
the platforms position to have external contributions.

### Other Possible Features
- This tool can also be used to manage/update the plugin, e.g. if the plugin version
changes (or any other metadata), devices are added, etc. the tool could be used with
an `--update` flag to update appropriate components.
