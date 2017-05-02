#!/bin/bash

# Simple script for looping opendcre-core tests and keeping the logs.

# Usage: (Hacky but it's a start)

# Working directory is where the test Makefile lives.
# cd ~/src/vapor/opendcre-core/opendcre_southbound/tests.

# Manually remove previous results or move them somewhere else.
# rm -rf ~/test_loop/

# Set TOTAL below to the number of times to loop the test set.
# Set test_set below to the tests you would like to run.

# My copy of this script lives in ~/src/me/test_loop/loop.sh
# Run the tests: . ~/src/me/test_loop/loop.sh

# Output goes to $OUTPUT_DIR below.

# Args are currently unused, but that may change.
echo Argument Count: $#
echo Arguments: $@

for arg in "$@"
do
  echo "$arg"
done

set pipefail

# Main output directory. Hardcoded for now.
OUTPUT_DIR=$HOME/test_loop/output
mkdir -p $OUTPUT_DIR

# Test set to run.
declare -a test_set=("test-ipmi-endpoints-trusted-x64"
                    "test-ipmi-throughput-trusted-x64"
                    "test-ipmi-no-init-scan-trusted-x64"
                    "test-ipmi-device-registration-trusted-x64"
                    "test-ipmi-scan-cache-registration-trusted-x64"
                    "test-ipmi-endpoints-untrusted-x64"
                    "test-ipmi-throughput-untrusted-x64"
                    "test-ipmi-no-init-scan-untrusted-x64"
                    "test-ipmi-device-registration-untrusted-x64"
                    "test-ipmi-scan-cache-registration-untrusted-x64"
                    "test-ipmi-emulator-x64"
                    "test-ipmi-invalid-trust-x64"
                    )

# Number of times to loop the test set. Keep track of pass / fail.
TOTAL=10
PASS=0
FAIL=0
for i in $(seq -w 1 $TOTAL); do

    # Create an output directory for this test set.
    TEST_SET_OUTPUT_DIR=$OUTPUT_DIR/output$i
    mkdir -p $TEST_SET_OUTPUT_DIR
    echo ITERATION start: $i;

    # Return code for this test set.
    test_set_rc=0
    # clean-test on every test set iteration.
    make clean-test
    for tst in "${test_set[@]}"
    do
      # Output directory for this specific test.
      TEST_OUTPUT_DIR="$TEST_SET_OUTPUT_DIR"/"$tst"
      mkdir -p "$TEST_OUTPUT_DIR"
      echo Running test: $tst 2>&1 | tee "$TEST_OUTPUT_DIR"/console.txt
      # Run the test command. Check rc (return code).
      make $tst 2>&1 | tee -a "$TEST_OUTPUT_DIR"/console.txt

      # BE CAREFUL HERE: rc=$? is wrong.
      #[mhink@ion ~]$ set pipefail
      #[mhink@ion ~]$ false | tee ~/tmp.txt
      #[mhink@ion ~]$ echo $?
      #0
      #[mhink@ion ~]$ false | tee ~/tmp.txt
      #[mhink@ion ~]$ echo $PIPESTATUS
      #1

      rc=$PIPESTATUS
      echo test rc is: $rc | tee -a "$TEST_OUTPUT_DIR"/console.txt

      # Get the opendcre container logs for this test.
      # We could get others as well if we need to.
      TEST_LOG_DIR="$TEST_OUTPUT_DIR"/logs
      OPEN_DCRE_LOG_DIR="$TEST_LOG_DIR"/opendcre
      mkdir -p "$OPEN_DCRE_LOG_DIR"
      docker cp x64_opendcre-southbound-test-container_1:/logs "$OPEN_DCRE_LOG_DIR"

      # If the test set has not failed yet.
      if [ $test_set_rc -eq 0 ]
      then
        # If this test failed.
        if [ $rc -ne 0 ]
        then
          # Test set fails with the first non-zero test return code.
          test_set_rc=$rc
        fi
      fi
    done

    # Test set result.
    if [ $test_set_rc -eq 0 ]
    then
        echo ITERATION result $i: PASS | tee -a $TEST_SET_OUTPUT_DIR/result.txt
        PASS=$((PASS+1))
    else
        echo ITERATION result $i: FAIL | tee -a $TEST_SET_OUTPUT_DIR/result.txt
        FAIL=$((FAIL+1))
    fi
done
echo PASS $PASS | tee -a $OUTPUT_DIR/results.txt
echo FAIL $FAIL | tee -a $OUTPUT_DIR/results.txt
echo TOTAL $TOTAL | tee -a $OUTPUT_DIR/results.txt

