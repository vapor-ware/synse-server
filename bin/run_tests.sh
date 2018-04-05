#!/usr/bin/env bash

set -o errexit -o pipefail -x

mkdir -p results/$1

tox $1 | tee results/$1/test.out
