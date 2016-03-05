===========
IPMI Bridge
===========

About
-----
The Vapor IPMI bridge allows users of OpenDCRE to utilize both bus-bar-based power line communications, and LAN-based IPMI communications for equipment monitoring and management. The IPMI bridge is included with OpenDCRE v1.1.0 and later, and supports power control and status via IPMI using the OpenDCRE REST API.

Requirements
------------

- OpenMistOS must be connected to a wired LAN network that can reach all BMCs configured to be managed over OpenDCRE.
- Knowledge of BMC IP addresses, authentication, integrity and encryption types as well as usernames and passwords (where applicable) required.
- IPMI 2.0 Authentication types supported:
    - ``NO_AUTHENTICATION_ALGORITHM`` : No authentication used to establish IPMI session.
    - ``RAKP_HMAC_SHA1`` : RAKP HMAC SHA1-128 authentication used to establish IPMI session.
- IPMI 2.0 Integrity types supported:
    - ``NO_INTEGRITY_ALGORITHM`` : No integrity algorithm used in IPMI session.
    - ``HMAC_SHA1_96`` : HMAC SHA1-96 used to verify packet integrity.
- IPMI 2.0 Encryption types supported:
    - ``NO_ENCRYPTION_ALGORITHM`` : No encryption used to ensure confidentiality of IPMI packets in session.
    - ``AES_CBC_128`` : AES 128-bit CBC encryption used to ensure confidentiality of IPMI packets.

Configuration
-------------
The Vapor IPMI bridge is configured via the ``bmc_config.json`` file, which must be placed in the top level of the OpenDCRE distribution.  An example file, ``bmc_config_sample.json`` is included with OpenDCRE (located in the ``opendcre_southbound`` directory), and may be modified to one's environment.

All IPMI BMCs successfully configured will show up on a ``scan`` command result as devices under ``board_id`` 40000000.
::

    {
      "bmcs": [
        {
          "bmc_ip": "192.168.1.118",
          "username": "ADMIN",
          "password": "ADMIN",
          "auth_type": "RAKP_HMAC_SHA1",
          "integrity_type": "HMAC_SHA1_96",
          "encryption_type": "AES_CBC_128"
        },
        {
          "bmc_ip": "192.168.1.119",
          "username": "root",
          "password": "vapor",
          "auth_type": "RAKP_HMAC_SHA1",
          "integrity_type": "HMAC_SHA1_96",
          "encryption_type": "AES_CBC_128"
        }
      ]
    }

For each BMC supported, an entry is added to the ``bmcs`` list above.  Each entry must include:

- ``bmc_ip`` - the IP address (as a string) corresponding to the BMC to be managed.  IP address must be reachable by OpenMistOS.
- ``username`` - the username to use in connecting to the BMC - may be an empty string if no username is used.
- ``password`` - the password to use in connecting to the BMC - may be an empty string if no username is used.
- ``auth_type`` - the type of authentication to use in connecting to the BMC, supported values:
    - ``NO_AUTHENTICATION_ALGORITHM``
    - ``RAKP_HMAC_SHA1``
- ``integrity_type`` - the type of integrity validation to use in communicating with the BMC, supported values:
    - ``NO_INTEGRITY_ALGORITHM``
    - ``HMAC_SHA1_96``
- ``encryption_type`` - the type of encryption to use in communicating with the BMC, supported values:
    - ``NO_ENCRYPTION_ALGORITHM``
    - ``AES_CBC_128``

If a field is missing, or the ``bmc_config.json`` file is improperly formatted, OpenDCRE IPMI capabilities will not be available.

Once the configuration file has been successfully edited, rebuild the OpenDCRE Docker container, and verify the configured BMC devices are returned via a ``scan`` command.

Each BMC device will show up as a board, with ``board_id`` in the range of ``40000001``..``40FFFFFF``.

OpenDCRE commands may be issued against IPMI and PLC devices without change in command format.

Tested BMCs
-----------
OpenDCRE v1.2 has been tested and verified to be compatible with IPMI 2.0 connections and commands for the following BMCs:

    - ASpeed AST2400 (via HPE CL7100)
    - Nuvoton WPCM450RA0BK (via SuperMicro X7SPA-HF)
    - ASpeed AST2050 (via Tyan S8812)
    - ASpeed AST1250 (via Freedom)

The OpenDCRE community welcomes testing and bug reports against other BMCs and system types.