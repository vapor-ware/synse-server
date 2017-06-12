#!/bin/bash

# The CEC board has a watchdog on it. After the CEC board gets the first
# message from the fa controllen, it activates a watchdog. When the watchdog
# detects that the fan controller has not sent a message for a minute it assumes
# the fan controller is dead and runs the fan at max. This script appeases the
# watchdog during development, for example when tearing down and setting up the
# containers.

while true ; do
  sudo -HE env PATH=$PATH PYTHONPATH="../protocols:${PYTHONPATH}" ./gs3fan.py get ;
  sleep 5 ;
done

