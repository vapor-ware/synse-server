===================================
OpenDCRE / OpenMistOS Release Notes
===================================

OpenDCRE v1.2.0 Release Notes
-----------------------------

March 5, 2016

The OpenDCRE v1.2.0 release is a significant release, adding a large set of new features to both OpenDCRE and OpenMistOS.

This release provides a long-awaited major update to the original OpenDCRE v1.x codebase, and has excellent feature, test, and usability enhancements.

Included in this release:

- OpenMistOS v1.1.0
    - Kernel updated to Linux 4.1.17 for armv7l
    - Debian ``jessie`` (includes ``systemd`` support) - upgraded from ``wheezy`` in prior releases
    - Docker v1.10.1 and Docker Compose version v1.6.2
- OpenDCRE v1.2.0
    - IPMI 2.0 support added to IPMI bridge
    - Added support via PLC and IPMI for:
        - `fan` command (fan control)
        - `led` command (chassis "identify" LED control)
        - `location` command (physical and intra-chassis location)
        - `asset` command (asset information)
        - `boot_target` command (boot target selection)
        - `temperature`, `humidity`, `fan_speed` sensor support added
    - Normalization of OpenDCRE API command layout for consistency and future functionality
    - PLC communications (devicebus_interfaces) for v1 RPI HAT finalized
    - Emulator enhancements for new functionality
    - Improvements to code organization, PEP8 compliance, documentation
    - Testing via docker-compose (supported on RPI and Linux/MacOS)

Contributors to this release:

    - Andrew Cencini, Vapor IO (maintainer)
        - IPMI, PLC, code, test enhancements
    - Klemente Gilbert-Espada, Vapor IO (docs, contributor)
        - RPI ``pyserial`` bugfix, Sphinx documentation
    - Erick Daniszewski, Vapor IO (contributor)
        - Test enhancements, bugfixes

Special thanks to early adopters and testers of OpenDCRE.
