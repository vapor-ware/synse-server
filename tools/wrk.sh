#!/bin/bash

# basic script for testing endpoints with wrk - this should be modified appropriately
# when running against different back-ends (i2c, rs485, emulated, live, ...)

if [[ -z $(which wrk) ]]
then
    echo "wrk not installed -- see https://github.com/wg/wrk"
    exit -1
fi


docker run -p 5000:5000 -e VAPOR_DEBUG=true --name synse -d vaporio/synse-server:latest emulate-rs485

END=3

sleep 3

echo "===> TEST"
curl -s localhost:5000/synse/1.4/test | head -n 10
echo -e "\n..."
for i in $(seq 1 ${END})
do
    echo -e "\nRun ${i}"
    echo "-----------------"
    wrk -t12 -c400 -d30s http://localhost:5000/synse/1.4/test
done


echo "===> SCAN"
curl -s localhost:5000/synse/1.4/scan | head -n 10
echo -e "\n..."
for i in $(seq 1 ${END})
do
    echo -e "\nRun ${i}"
    echo "-----------------"
    wrk -t12 -c400 -d30s http://localhost:5000/synse/1.4/scan
done

echo "===> FORCE SCAN"
curl -s localhost:5000/synse/1.4/scan/force | head -n 10
echo -e "\n..."
for i in $(seq 1 ${END})
do
    echo -e "\nRun ${i}"
    echo "-----------------"
    wrk -t12 -c400 -d30s http://localhost:5000/synse/1.4/scan/force
done

echo "===> READ"
curl -s localhost:5000/synse/1.4/read/humidity/rack_1/50000001/0001 | head -n 10
echo -e "\n..."
for i in $(seq 1 ${END})
do
    echo -e "\nRun ${i}"
    echo "-----------------"
    curl -s localhost:5000/synse/1.4/read/humidity/rack_1/50000001/0001
    wrk -t12 -c400 -d30s http://localhost:5000/synse/1.4/read/humidity/rack_1/50000001/0001
done


docker rm -f synse