# Tests
## Summary
Most projects in the Synse platform already have good test coverage. In addition to
maintaining and improving the existing tests, a new class of tests will be added for
testing the services in a Kubernetes deployment.

## High Level Work Items
- Maintain existing tests, improve them where possible
- Clean up old tests to use more standardized approaches
- Add deployment/failure tests with tools like `kubetest`

## Proposal
The primary item here is the addition of a new class of tests: deployment and failure
testing. These tests should be executed in CI and should test that the service works
in its Kubernetes deployment as expected. 

Additionally, it should tests failure scenarios. In particular, failing a service and
ensuring that any dependent services handle the failure correctly and recover when the
failed service is restarted.

To do this, we can leverage the [kubetest](https://github.com/vapor-ware/kubetest) project.

Not all projects will need these deployment and failure tests in place for the v3 release,
however all projects should have a high level test plan which identifies what will need
to be tested and how. Tests can be added after initial release.