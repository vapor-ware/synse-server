#!/bin/bash

# synse.sh
#
# This script is the entry point script for the Synse Server docker
# images. It is used to start Synse Server and to optionally start
# an instance of the emulator plugin alongside it.
#
# ---------------------------------------------------------------------
# Copyright (C) 2015-18  Vapor IO
#
# This file is part of Synse.
#
# Synse is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Synse is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Synse.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------------------------------------------
set -o errexit -o pipefail

version="$(python -c "import synse ; print(synse.__version__)")"
pid=0

# help
# ----
#   display usage information
function -h {
cat <<USAGE
   __
  / _\_   _ _ __  ___  ___
  \ \| | | | '_ \/ __|/ _ \\
  _\ \ |_| | | | \__ \  __/
  \__/\__, |_| |_|___/\___| v${version}
      |___/

    Vapor IO

  Synse provides a unified API for the monitoring and control of
  data center and IT equipment, including reading sensors and
  server power control.

  By default only the Synse service will run, but additional
  subcommands can be specified to modify the behavior - for
  example, starting up an emulator.

  USAGE:
    docker run vaporio/synse-server [flag | subcommand]

  Flags:
    --help, -h     Show this message.
    --version, -v  Show the version of Synse.

  Subcommands:
    enable-emulator
            Start a built-in emulator to provide mock data to Synse.
            This can be useful for testing and learning about Synse.
            A default emulator configuration is provided, but different
            configurations can be used by either volume mounting in
            custom configurations (to /synse/synse/emulator/config)
            or by building a custom image with those configs already
            changed.

USAGE
exit 0
}; function --help { -h ;}


# version
# -------
#   show the version of synse
function -v {
    echo "${version}"
}; function --version { -v ;}


# enable background emulator
# --------------------------
#   start the background process emulator using the emulator
#   configurations found in /synse/synse/emulator/config
function enable-emulator {
    if [ "$(which emulator)" ]; then
        # the emulator binary is downloaded and installed into /usr/local/bin
        # in the dockerfile. the configs for it are set via ENV variable in
        # the dockerfile as well.
        emulator 1>&2 &
    else
        echo "This Synse Server image does not contain the emulator."
        echo "Try using a non 'slim' Synse Server image for emulator"
        echo "support."
        exit 1
    fi
}

# signal exit
# -----------
#   exit when a signal is trapped. we need to do this here since
#   docker/kubernetes send a signal to PROC 1 in the container,
#   which would be this script.
function signal_exit {
    echo "caught signal - exiting"
    if [ ${pid} -ne 0 ]; then
        kill -SIGTERM "$pid"
    fi
    exit 1
}

trap signal_exit SIGINT SIGTERM

# if any arguments were passed in, act on them now.
for var in "$@"
do
    "$var"
done

# start synse
python synse &
pid="$!"

# wait forever
while true
do
    tail -f /dev/null & wait ${!}
done