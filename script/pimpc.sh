#!/bin/bash

usage="Usage: "$0" <port> <add|replace> <filename|dirname>"

if [ $# -ne 3 ]
then 
    echo $usage
    exit 1
fi
max_file=500




case $2 in
    "add")
	mpc -p ${1} add "$3"
	;;
    "replace")
	mpc clear
	mpc -p ${1} add "$3"
	;;
    *)
	echo $usage
	exit 1;
	;;
esac

