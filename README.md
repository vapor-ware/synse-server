# Synse Server 2.0 *DEV*

NOTE: this is the development branch for synse-server v2.0. the architecture here
is pretty different from the v1.X branches. **this branch is NOT intended to be merged
into master here.** it is just meant to be a source-controlled place for development. 

once it comes time to release v2, what will likely need to happen is this branch will
get copied into the public synse server repo as a branch. that will probably be a bit
of a headache, but once that is done and synse server v2.0 is live, then we will no
longer have to maintain a public and private repo for synse server and life will be 
much simpler.



## TODO:
below is a list of things that still needs to be done. it is not exhaustive, but 
provides a decent overview of what areas still need work. this will be updated as
progress is made/as new items are needed.


__api/server__
- [ ] finalize synse 2.0 JSON api
    - [ ] what commands will be supported?
    - [ ] what is the command behavior?
- [ ] support for commands (depending on the finalized JSON api)
    - [ ] HEALTH
        - [ ] determine response scheme
        - [ ] determine response data
        - [ ] add command handling / route
        - [ ] support all permutations (rack/board/device)
    - [ ] INFO
        - [ ] determine response scheme
        - [ ] determine response data
        - [ ] add command handling / route
        - [ ] support all permutations (rack/board/device)
    - [ ] LOCATION
        - [ ] determine response scheme
        - [ ] determine response data
        - [ ] add command handling / route
        - [ ] support all permutations (rack/board/device)
    - [ ] READ
        - [ ] determine response scheme
        - [ ] determine response data
        - [ ] add command handling / route
        - [ ] support all permutations (rack/board/device)
    - [ ] SCAN
        - [ ] determine response scheme
        - [ ] determine response data
        - [ ] add command handling / route
        - [ ] support all permutations (rack/board/device)
    - [ ] TEST
        - [ ] determine response scheme
        - [ ] determine response data
        - [ ] add command handling / route
        - [ ] support all permutations (rack/board/device)
    - [ ] TRANSACTION
        - [ ] determine response scheme
        - [ ] determine response data
        - [ ] add command handling / route
        - [ ] support all permutations (rack/board/device)
    - [ ] VERSION
        - [ ] determine response scheme
        - [ ] determine response data
        - [ ] add command handling / route
        - [ ] support all permutations (rack/board/device)
    - [ ] WRITE
        - [ ] determine response scheme
        - [ ] determine response data
        - [ ] add command handling / route
        - [ ] support all permutations (rack/board/device)
    - [ ] GROUP
        - [ ] determine response scheme
        - [ ] determine response data
        - [ ] add command handling / route
        - [ ] support all permutations (rack/board/device)
- [ ] add JSON error responses
- [ ] add internal error codes for error responses (easier for error id and debug)


__configuration__
- [ ] finalize configuration scheme design
- [ ] design out configuration story (important - config was confusing w/ v1.X)
- [ ] add in configuration handling/parsing


__plugins__
- [ ] write emulator plugin (using SDK?)
    - [ ] read
    - [ ] write
    - [ ] metainfo
    - [ ] transaction check
- [ ] port existing backends to plugins
    - [ ] plc
    - [ ] ipmi
    - [ ] rs485
    - [ ] i2c
    - [ ] snmp
    - [ ] redfish


__documentation__
- [ ] add comments to emulator configuration
- [ ] add README describing the emulator and how it works
- [ ] fill out all python docstrings
- [ ] write out documentation (readthedocs)
- [ ] write out all READMEs


__testing__
- [ ] unit tests for everything
- [ ] add in code coverage/other reporting
- [ ] integration testing
- [ ] test synse server w/ and w/o NGINX in front of it
- [ ] set up circleci testing
- [ ] run performance tests against it on a VEC


__misc__
- [ ] write docker files / compose files for
    - [ ] production (release)
    - [ ] development (dev)
    - [ ] testing
    - [ ] linting
- [ ] try to optimize dockerfile(s) 
- [ ] cleaning / organization
- [ ] linting
