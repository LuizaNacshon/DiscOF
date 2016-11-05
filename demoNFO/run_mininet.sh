#!/bin/bash


for ((n=0;n<1;n++))
do


 sudo java -jar `pwd`/floodlight/target/floodlight.jar > `pwd`/logs/floodlight.out 2> `pwd`/logs/floodlight.err < /dev/null &
 pidcontroller=$!
 echo "ran controller"
 echo $n
 sleep 20;
 echo "sleep 20"
 sudo python `pwd`/NFO/run_pings.py $n  >`pwd`/logs/run_pings.out 2> `pwd`/logs/run_pings.err < /dev/null &
 pidpings=$!
 echo "ran run_pings"
 echo $n
 sudo python `pwd`/NFO/mainNFO.py $n  >`pwd`/logs/mainNFO.out 2> `pwd`/logs/mainNFO.err < /dev/null &
 pidnfo=$!
 echo "main NFO"
 echo $n
 sleep 3000;
 echo "sleep 3000"
 
 sudo pkill -f run_pings.py
 sudo pkill -f mainNFO.py
 sudo pkill -f python
 sleep 2;
 sudo echo 3 | sudo tee /proc/sys/vm/drop_caches
 sleep 3;
 sudo pkill -9 -f "sudo mnexec"
 
 sleep 20;
 sudo pkill -f java
 sudo pkill -f python
 sudo pkill -f ovs-controller
 sudo kill -KILL $pidcontroller
 sudo kill -KILL $pidpings
 sudo kill -KILL $pidnfo
 sleep 20;
done


