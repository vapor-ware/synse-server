# Scaffolding
## Summary
This document provides suggestions for project organization, tooling, and general
development flow. These are currently just suggestions and may need some experimentation
to determine whether they are worthwhile.

## High Level Work Items
- Determine if there are better tools/flows for developing Synse components
- Implement any of the above tools/flow, if any are found to be worthwhile

## Proposal
As the number of our repositories continue to grow, it is important to take the time
to make sure we keep things as standardized and automated as possible. Finding tooling
and workflows to minimize friction during development makes projects easier to maintain.

Below are some tools and processes that we can investigate to see if they are worthwhile
for our development flow.

**Tooling**

- [pre-commit](https://pre-commit.com/): a framework for managing and maintaining multi-language
  pre-commit hooks
- [goreleaser](https://goreleaser.com/): a release automation tool for Go projects
- [black](https://github.com/ambv/black): automatic python code formatter (similar to `go fmt`)
  which would obviate the need for slower tools like pylint 

**CI/CD**

- [Jenkins CI](https://build.vio.sh/blue/pipelines): we should continue to use our build server
  for all projects and automate testing, linting, image builds, and releases
- [kubetest](https://github.com/vapor-ware/kubetest): test Kubernetes deployments
