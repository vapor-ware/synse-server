=============
Release Notes
=============

v1.3.0
======

*February 21, 2017*

The OpenDCRE 1.3.0 release is another significant release which brings many changes to the OpenDCRE code base.
Along with significant code refactoring, cleanup, documentation, and testing, this release brings in Redfish support.

.. note::
    Redfish support should be considered a beta feature as of v1.3.0


Changelog
^^^^^^^^^

- Generalization of the underlying devicebus model. This makes it easier to add support for new protocols / devices
  moving forward.
- Added command dispatching from OpenDCRE endpoints to the new underlying devicebus model.
- Improvements to OpenDCRE configuration which allow for default and override configs.
- Switched internal IPMI back-end from custom C implementation to OpenStack's `pyghmi <https://github.com/openstack/pyghmi>`_
- [BETA] Redfish support in OpenDCRE

    - Standalone Redfish Emulator
    - Redfish Device integration into OpenDCRE
    - Test cases for the emulator as well as OpenDCRE configured under Redfish

- Various bug fixes and performance fixes.
- Improvements to code organization, formatting, and documentation.
- Dockerfile optimizations.
- Additional test cases added and existing test cases expanded.

Contributors
^^^^^^^^^^^^
- Andrew Cencini, Vapor IO
- Erick Daniszewski, Vapor IO
- Matthew Hink, Vapor IO
- Klemente Gilbert-Espada, Vapor IO
- Kyler Burke, Vapor IO
- Morgan Mills, Vapor IO / Bennington College
- Linh Hoang, Vapor IO / Bennington College


v1.2.0
======

*March 5, 2016*

The OpenDCRE v1.2.0 release is a significant release, adding a large set of new features to OpenDCRE.

This release provides a long-awaited major update to the original OpenDCRE v1.x codebase, and has excellent feature,
test, and usability enhancements.


Changelog
^^^^^^^^^

- IPMI 2.0 support added to IPMI bridge
- Added support via PLC and IPMI for

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


Contributors
^^^^^^^^^^^^
- Andrew Cencini, Vapor IO (maintainer)
    - IPMI, PLC, code, test enhancements
- Klemente Gilbert-Espada, Vapor IO (docs, contributor)
    - RPI ``pyserial`` bugfix, Sphinx documentation
- Erick Daniszewski, Vapor IO (contributor)
    - Test enhancements, bugfixes

Special thanks to early adopters and testers of OpenDCRE.
