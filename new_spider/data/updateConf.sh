#!/bin/sh

if [ "$#" -eq 0 ]; then
echo "Usage: ./updateConf.sh /sz_azero/config.json"
exit 0
fi

CONFIG_FILE=$1

#Update device mac address to /sz_azero/sai_config/config.json
MACADDR=`ifconfig | grep wlan0 | awk '{print $5}'`
CLIENTID=5dada2f972857b00076b3d24
#CUEI=`cat /data/cuei`

FIRMWARE_VERSION=`cat /etc/version | grep VERSION_TIME | awk -F= '{print $2}'`
VOL_NUM=`amixer cget name='Master Volume' | grep values | tail -n 1  | awk -F = '{print $2}'`
WIFI_SSID=`iw dev wlan0 link | grep SSID | awk '{print $2}'`
DEVICE_ID=${MACADDR}

BLE_CHK=`cat /sys/class/rfkill/rfkill0/state`
if [ $? -eq 0 ]; then
if [ "$BLE_CHK" -eq "0" ]; then
BLE_STATUS=false
else
BLE_STATUS=true
fi
fi

cnt=1
while true
do
	IP_ADDR=`ifconfig -a | grep inet | grep -v 127.0.0.1 | grep -v inet6 | awk '{print $2}' | tr -d "addr:"`	
	echo "$IP_ADDR"
	if [ "$IP_ADDR" = "" ]
	then
		sleep 1
		cnt=$((cnt + 1))
		if [ $cnt -gt 9 ]; then
			break
		fi
	else
		break
	fi
done

#sed -i "s/clientId\"\:\ \".*\"/clientId\"\:\ \"${CLIENTID}\"/" ${CONFIG_FILE}
sed -i "s/deviceSerialNumber\"\:\ \".*\"/deviceSerialNumber\"\:\ \"${MACADDR}\"/" ${CONFIG_FILE}

sed -i "s/firmwareVersion\"\:\ .*\,/firmwareVersion\"\:\ ${FIRMWARE_VERSION}\,/" ${CONFIG_FILE}

sed -i "s/volume\"\:\ .*\,/volume\"\:\ ${VOL_NUM}\,/" ${CONFIG_FILE}

sed -i "s/wifi_ssid\"\:\ \".*\"/wifi_ssid\"\:\ \"${WIFI_SSID}\"/" ${CONFIG_FILE}

sed -i "s/bluetooth_active\"\:\ .*\,/bluetooth_active\"\:\ ${BLE_STATUS}\,/" ${CONFIG_FILE}

sed -i "s/device_id\"\:\ \".*\"/device_id\"\:\ \"${DEVICE_ID}\"/" ${CONFIG_FILE}
sed -i "s/mac\"\:\ \".*\"/mac\"\:\ \"${MACADDR}\"/" ${CONFIG_FILE}
sed -i "s/ip\"\:\ \".*\"/ip\"\:\ \"${IP_ADDR}\"/" ${CONFIG_FILE}

