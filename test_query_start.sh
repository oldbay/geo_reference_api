#!/bin/bash

if [ -f db/data.sqlite ];then
    rm db/data.sqlite
fi
python3 queries.py