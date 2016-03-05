==================================
Building OpenDCRE Docker Container
==================================

Building a modified OpenDCRE container is a fairly straightforward process.  First, clone the `OpenDCRE GitHub repository`__ to a location on OpenMistOS.

.. _OpenDCRE: https://github.com/vapor-ware/OpenDCRE

__ OpenDCRE_

Next, to build a custom distribution of OpenDCRE (for example, to include site-specific TLS certificates, IPMI BMC configuration, or to configure nginx to use site-specific authn/authz), the included Dockerfile can be used to package up the distribution.

In the simplest case, from the opendcre directory:
::

    docker build -t opendcre:custom-v1.2.0 -f Dockerfile.rpi .

Apply whatever tag is most descriptive for the custom image.

From this point, test and run OpenDCRE to ensure the changes were successful.