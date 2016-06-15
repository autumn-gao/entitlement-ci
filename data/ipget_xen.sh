#!/bin/sh
# return xenserver guest ip by mac address

mac=$1
if [[ -z $mac ]]; then
   echo "mac address is null."
   exit 1
fi

if ! rpm -qa |grep nmap ;then
   echo "need nmap rpmball installed."
   exit 1
fi


local_hostip=`ifconfig  | grep 'inet ' | grep -v '127.0.0.1' | grep -v '192.168' | awk '{ print $2 }'`
ipaddr=`ip route |grep xenbr0 | grep $local_hostip | awk {'print $1'}`


if [[ -n $ipaddr ]]; then
   output=$(nmap -sP -n $ipaddr | grep -i -B 2 $mac)
   if [[ -n $output ]]; then
      hostip=$(echo $output | sed -e 's/.* \([0-9]*\.[0-9]*\.[0-9]*\.[0-9]*\).*/\1/')
   else
      echo "can not get ip by mac: $mac"
   fi
else
   echo "no scanner port found"
fi

echo $hostip
