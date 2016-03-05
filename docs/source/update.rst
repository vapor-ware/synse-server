=================
Updating OpenDCRE
=================

OpenDCRE Updates
----------------

In OpenMistOS, upgrades to OpenDCRE may be carried out by updating the OpenDCRE docker container.  To do this, first stop OpenDCRE.

Then, log in to Docker Hub (assumes OpenMistOS has Internet access):

``$ docker login``

(enter your Docker Hub username, password and email address)

``$ docker pull vaporio/opendcre``

If an update is available, the latest version of opendcre will be pulled down to OpenMistOS.

Finally, start OpenDCRE again.

OpenMistOS Updates
------------------

To update OpenMistOS:

``$ sudo apt-get update && sudo apt-get upgrade``
