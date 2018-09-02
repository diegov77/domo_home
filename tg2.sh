#!/bin/bash
to=$1
msg=$2
tgpath=/home/pi/tg
cd ${tgpath}
cmd="bin/telegram-cli -W -k server.pub -e \"msg $to $msg\""
eval $cmd