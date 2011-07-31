#!/bin/bash

# Script used in Nautilus. To associate this script to mimetypes, modify file '~/.local/share/applications/mimeapps.list'
if [ $# -ne 1 ]
then 
    echo "Usage: "$0" <filename>"
    exit 1
fi
max_file=500
echo $1 | xargs -I{} find "{}" \
    -iname "*.flac" -o -iname "*.mp3" -o -iname "*.ogg" \
    | head -n $max_file | sort \
    | mpc add
