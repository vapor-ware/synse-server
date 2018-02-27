#!/bin/bash
# ---------------------------------------------------------------------
# Copyright (C) 2015-18  Vapor IO
#
# This file is part of Synse.
#
# Synse is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
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

version="$(python /synse/synse/version.py)"

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
    --help | -h     Show this message.
    --version | -v  Show the version of Synse.

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
    (cd emulator ; PLUGIN_DEVICE_CONFIG=config ./emulator 1>&2 &)

    # FIXME - this sleep is just added in for safety to make sure that
    # the emulator, if started, has enough time to start up and create
    # the socket that synse will use to communicate with it.
    sleep 1
}


# if any arguments were passed in, act on them now.
for var in "$@"
do
    "$var"
done

# start synse
python /synse/runserver.py