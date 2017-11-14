#!/usr/bin/env bash

set -o errexit -o pipefail -x

handle_error() {
    local exit_code=$1 && shift
    echo -e "\nSUBSHELL ERROR\t$exit_code"
    exit ${exit_code}
}

set -o errtrace
trap 'handle_error $?' ERR


function load() {
    docker volume create ${1}
    docker run -v ${1}:/scratch --name helper busybox true
    docker cp ${2} helper:/scratch
    docker rm helper
}

function run_test {
    # first, remove any stale containers that might be hanging around.
    docker rm -f $(docker ps -aq) || true

    # then, run the test
    docker-compose -f compose/$1 up \
            --build \
            --abort-on-container-exit \
            --exit-code-from synse-server
}

function main {
  load synse-server-source .

  # run the tests and capture the test results
  run_test "$1_test.circleci.yml"
  docker cp synse-server:/code/results/. /tmp/test-results
}


function msg { out "$*" >&2 ;}
function err { local x=$? ; msg "$*" ; return $(( $x == 0 ? 1 : $x )) ;}
function out { printf '%s\n' "$*" ;}

if [[ ${1:-} ]] && declare -F | cut -d' ' -f3 | fgrep -qx -- "${1:-}"
then "$@"
else main "$@"
fi