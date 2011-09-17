#!/bin/bash

usage="Usage: "$0" <port> <add|replace> <filename|dirname>"

if [ $# -ne 3 ]
then 
    echo $usage
    exit 1
fi
max_file=500

add()
{
    find "${2}" \
	-iname "*.flac" -o -iname "*.mp3" -o -iname "*.ogg" \
	| head -n $max_file | sort \
	| mpc -p ${1} add
}


case "$2" in
    "add")
	add $1 $3
	;;
    "replace")
	mpc clear
	add $1 $3
	;;
    *)
	echo $usage
	exit 1;
	;;
esac

