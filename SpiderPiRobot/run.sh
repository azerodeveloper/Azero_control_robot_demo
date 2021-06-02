#! /bin/bash

while :
do
	sleep 1
	ping -c 1 www.baidu.com > /dev/null 2>&1

	if [ $? -eq 0 ];then
		echo "Network connect success."
		/usr/bin/python3 /home/pi/Desktop/SpiderPiRobot/python/connect_success.py &
		ps -ef | grep spider | grep -v grep
		# 结果不包含spider时，$?=1
		if [ $? -ne 0 ]; then
			echo "Start process."
			# /usr/bin/python3 /home/pi/Desktop/SpiderPiRobot/python/spider.py &
			/usr/bin/python3 /home/pi/Desktop/SpiderPiRobot/python/welcome.py &
		else
			echo "The spider script is already running..."
		fi
		break
	else
		echo "Network connecting..."
	fi
done

