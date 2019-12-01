#!/bin/bash

rm db.sqlite || echo db.sqlite  not found
env GEO_REF_API_CONF=conf.json python3 req_server.py
