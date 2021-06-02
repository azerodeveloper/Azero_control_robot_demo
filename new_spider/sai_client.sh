#!/bin/sh
cd /home/pi
#export LD_LIBRARY_PATH=./lib
sudo LD_LIBRARY_PATH=$PWD/lib ./sai_client > my.log
