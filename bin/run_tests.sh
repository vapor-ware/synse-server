#!/usr/bin/env bash

# run_tests.sh
#
# This script runs the tests via tox, as specified by the argument
# passed to the script, and outputs the results both to console
# and to file in the results/ directory.
#

set -o errexit -o pipefail -x

mkdir -p results/$1

tox $1 | tee results/$1/test.out
