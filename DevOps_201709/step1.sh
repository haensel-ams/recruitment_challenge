#!/bin/bash

echo -n "Running step1... "

sleep `expr $RANDOM / 4 + 3600`

if [ $RANDOM -gt 29000 ]; then
    echo "FAILED!"
    exit 1
fi

echo "DONE!"

