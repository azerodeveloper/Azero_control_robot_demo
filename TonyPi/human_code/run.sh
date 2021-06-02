#! /bin/bash

while :
do
	sleep 1
	ping -c 1 www.baidu.com > /dev/null 2>&1

	if [ $? -eq 0 ];then
		echo "Network connect success."
		/usr/bin/python3 /home/pi/human_code/network_connect.py &
		ps -ef | grep tonipi | grep -v grep
		# 结果不包含spider时，$?=1
		if [ $? -ne 0 ]; then
			echo "Start process."
			/usr/bin/python3 /home/pi/human_code/tonipi.py &
			/usr/bin/python3 /home/pi/human_code/tonipi_welcome.py &
			# /usr/bin/python3 /home/pi/human_code/tonipi_welcome_hu.py &
		else
			echo "The tonipi script is already running..."
		fi
		break
	else
		echo "Network connecting..."
	fi
done
