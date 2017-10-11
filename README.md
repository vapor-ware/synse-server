

TODO:

[ ] write unit tests
[ ] write integration tests
[√] update emulator for functional:
    [√] writes
    [√] transaction checks
    [√] reads
    [√] metainfo
[ ] add comments to emulator configuration
[ ] README for how emulator works
[√] set up proper error handling for the emulator
[ ] figure out what the response should be / where the data comes from for
    [ ] info
    [ ] health
    [ ] location
[ ] add commands for:
    [ ] health
    [ ] info
    [ ] location
    [√] read
    [√] scan
    [√] test
    [√] transaction
    [√] version
    [√] write
[ ] complete command permutations/filtering for
    [ ] scan
    [ ] info
    [ ] location?
    [ ] health?
[√] add error json responses (404, 500)
[√] proper error handling for Synse - should use sanic.ServerError.. or a subclass of it for propagation of ids
[ ] fill out all python docstrings
[ ] write out documentation
[√] get dockerfiles/compose files written for
    [√] prod
    [√] dev
    [√] test
    [√] lint
[√] try to optimize dockerfile(s)
[ ] test synse w/ and w/o NGINX in front of it
[ ] finish specifying the config
[ ] cleaning
[ ] linting
[ ] run perf tests on it on a VEC


[ ] convert existing 1.4 backend functionality to bg processes
    [ ] plc
    [ ] ipmi
    [ ] rs485
    [ ] i2c
    [ ] redfish


[ ] create new repo?
[ ] set up circleci testing 