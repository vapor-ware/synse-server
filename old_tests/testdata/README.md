This directory is used to house runtime-generated test data pertaining to testing
with unix sockets. Unix socket paths have a character limitation which the builtin
pytest [`tmpdir`](https://docs.pytest.org/en/2.8.7/tmpdir.html) fixture will often
exceed because of how it generates unique numbered directories for each test case, e.g.

```
tmpdir = local('/var/lib/jenkins/workspace/-server_update-test-dir-fixtures/tests/testdata/test_register_unix_plugin_no_c0')
```

For testing purposes, socket generation should be done via the `tmpsocket` fixture,
defined in `conftest.py`. Tests which require a temporary directory but do not use
sockets should use pytests' `tmpdir` fixture.