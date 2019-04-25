#!/usr/bin/env bash

# install_emulator.sh
#
# This script is used to install the latest release of the emulator
# plugin into the current working directory. This is used in the
# Synse Server Dockerfile, but can also be run locally.
#
# This script requires `curl` and `jq` to be installed.
#
# The following environment variables can be used with the script
# to modify the default behavior:
#   EMULATOR_BIN - the name of the emulator binary to download. see
#      https://github.com/vapor-ware/synse-emulator-plugin/releases
#      for the names of all available assets. (default: emulator_linux_amd64)
#   EMULATOR_OUT - the path to output the downloaded binary
#      (default: `./$EMULATOR_BIN`)
#
set -o errexit -o pipefail

EMULATOR_REPO=vapor-ware/synse-emulator-plugin

EMULATOR_BIN=${EMULATOR_BIN:-"emulator_linux_amd64"}
EMULATOR_OUT=${EMULATOR_OUT:-""}

# Get the GitHub release data for the Synse Emulator Plugin repo.
data=$(curl -s https://api.github.com/repos/${EMULATOR_REPO}/releases/latest)

# Get the URL for the latest release asset binary.
bin_url=$(echo ${data} | jq '.assets[] | select(.name | contains("linux_amd64")) | .url ' | tr -d '"')

# Download the binary
curl -L -H "Accept: application/octet-stream" -o ${EMULATOR_BIN} ${bin_url}
chmod +x ${EMULATOR_BIN}

if [[ "$EMULATOR_OUT" ]]; then
    mv ${EMULATOR_BIN} ${EMULATOR_OUT}
fi
