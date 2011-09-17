#!/bin/bash

usage="Usage: "$0" <add|replace> <filename|dirname>"

if [ $# -ne 2 ]
then 
    echo $usage
    exit 1
fi
max_file=500

add()
{
    find "${1}" \
	-iname "*.flac" -o -iname "*.mp3" -o -iname "*.ogg" \
	| head -n $max_file | sort \
	| mpc add
}


case "$1" in
    "add")
	add $2
	;;
    "replace")
	mpc clear
	add $2
	;;
    *)
	echo $usage
	exit 1;
	;;
esac

