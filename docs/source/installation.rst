=============================
Getting OpenDCRE & OpenMistOS
=============================

Requirements
============

Hardware Requirements
---------------------

- Raspberry Pi 2 Model B (other Raspberry Pi versions are not supported).
- 4GB Micro SD card - 8GB or larger recommended.
- 5V Micro USB power source.
- Wired ethernet connection (wireless supported but not recommended).
- OpenDCRE HAT (optional)
- DC Bus Bar for power line communications (optional)
- IPMI 1.5-compliant BMC for IPMI bridge (optional)
- HDMI/HDMI-VGA video cable & monitor (optional)

Software Requirements
---------------------

- OpenMistOS v1.0.0 or later.

Download and Install
====================

Download
--------

- `Download OpenMistOS`__ , and decompress the .img file.  `OpenDCRE Source`__ on GitHub.

.. _OpenMistOS: http://www.vapor.io/file/2015/11/OpenMistOS-v1.0.0.img.tar.gz

.. _OpenDCRE: https://github.com/vapor-ware/OpenDCRE 

__ OpenMistOS_

__ OpenDCRE_

Install
-------

- Insert Micro SD card into card reader, and determine the SD card device:
    - MacOS: 
        - ``sudo diskutil list``
    - Linux:  
        - ``sudo fdisk -l``
- Use ``dd`` to write image to card:
    - MacOS: 
        - ``sudo dd if=<.img file> of=<sd card device> bs=4m``
    - Linux: 
        - ``sudo dd if=<.img file> of=<sd card device> bs=4M``
    - Note:
        - ``<.img file>`` is the path and filename of the decompressed OpenMistOS .img downloaded above.
        - ``<sd card device>`` is the SD card device determined in the previous step. (e.g. - /dev/disk1)

When executing the above commands, if an error is returned similar to: ``dd: <sd card device>: Resource busy`` then the SD card must be unmounted.To do this, identify the SD card partition (can use ``df -h`` for this, or the results from determining the SD card device, above), then unmount the partition:

- *MacOS*:
    - ``sudo diskutil unmount <sd card device>``
- *Linux*: 
    - ``sudo umount <sd card device>``

When ``dd`` is complete, OpenMistOS is ready to run from the SD card.  Plug the Raspberry Pi into the wired network, insert the Micro SD card, and power up the Raspberry Pi.

At completion of the boot process, the OpenMistOS device IP address is displayed on screen (if video connection is used); alternately, check DHCP or router logs to determine the IP address of the OpenMistOS device.

Login
-----

Ssh into the OpenMistOS device:

- *Username*:  ``openmistos``
- *Password*:  ``0p3ndcr3!``


The openmistos user has sudo rights on OpenMistOS.  It is recommended to **immediately** change the openmistos password to a new, secure, password.

**Note**: OpenMistOS, like other Raspberry Pi OSes, uses only the space required for the OS on the SD card. It is recommended to change this behavior so that the entire space on the SD card is used. To do this, enter the configuration menu on first login:

``$ sudo raspi-config``

In the configuration menu, there should be an option to use the entire disk. Once selected and confirmed, OpenMistOS will restart and the entire SD card will then be used.

Verification
------------
There are several methods for verifying that OpenDCRE is running properly.

Browser
-------

Navigate to:
::

    http://<openmistos ip address>:5000/opendcre/1.1/test

Output should be similar to:
::

    {
        "status": "ok"
    }

Command-Line
------------

Running:
``$ docker ps``

produces output similar to:
::

    CONTAINER ID        IMAGE                      COMMAND                CREATED          STATUS              PORTS                    NAMES
    a9419ff86502        vaporio/opendcre:latest    "./start_opendcre.sh   4 days ago       Up 4 days           0.0.0.0:5000->5000/tcp   opendcre

(when using the HAT)

or:
::

    CONTAINER ID        IMAGE                     COMMAND                CREATED             STATUS              PORTS                    NAMES
    2281101f6a60        vaporio/opendcre:latest   "./start_opendcre_em   4 days ago          Up 4 days           0.0.0.0:5000->5000/tcp   opendcre

(when using the emulator)

The OpenDCRE service starts automatically at boot; it can be started/stopped via the init.d daemon:

``$ sudo /etc/init.d/opendcre <start|stop>``

Logs
----

By default, OpenDCRE logs are placed in /var/log/opendcre .  Access, error and daemon logs are available for troubleshooting and analytics.
