#!/bin/bash

rm db.sqlite || echo db.sqlite  not found
env GEO_REF_API_CONF=conf.json ./req_server.py
