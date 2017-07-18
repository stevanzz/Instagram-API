#!/bin/bash

while true; do
	date +"%T"
	procs=`ps -ef | grep chrome  | grep -v "grep" |  awk '{print $2}'`
	if [ -z "$procs" ]; then
		echo "chrome process is not active"
	fi
	# for each PID in PIDs array
	for pid in $procs; do
		# get elapsed time in form mm:ss and remove ":" character
		# to make it easier to parse time 
		time=(`ps -o etime $pid | sed -e 's/[:-]/ /g'`)
		# get minutes from time
		min=${time[1]}
		echo $min
		# if proces runs 5 minutes then kill it
		if [ "$min" -gt "180" ]; then
			kill -9 $pid
		else
			echo "chrome process is running normally"
		fi
	done;

	procs=`ps -ef | grep chromedriver  | grep -v "grep" |  awk '{print $2}'`
        if [ -z "$procs" ]; then
                echo "chromedriver process is not active"
        fi
	# for each PID in PIDs array
        for pid in $procs; do
                # get elapsed time in form mm:ss and remove ":" character
                # to make it easier to parse time
                time=(`ps -o etime $pid | sed -e 's/[:-]/ /g'`)
                # get minutes from time
                min=${time[1]}
                echo $min
                # if proces runs 5 minutes then kill it
                if [ "$min" -gt "180" ]; then
                        kill -9 $pid
                else
			echo "chromedriver process is running normally"
		fi
        done;

	procs=`ps -ef | grep Xvfb  | grep -v "grep" |  awk '{print $2}'`
	if [ -z "$procs" ]; then
                echo "Xvfb process is not active"
        fi
	# for each PID in PIDs array
        for pid in $procs; do
                # get elapsed time in form mm:ss and remove ":" character
                # to make it easier to parse time
                time=(`ps -o etime $pid | sed -e 's/[:-]/ /g'`)
                # get minutes from time
                min=${time[1]}
                echo $min
                # if proces runs 5 minutes then kill it
                if [ "$min" -gt "180" ]; then
                        kill -9 $pid
		else
			echo "Xvfb process is running normally"
	        fi
        done;
	echo "-----------------------------------------------"
	sleep 3600
done;
