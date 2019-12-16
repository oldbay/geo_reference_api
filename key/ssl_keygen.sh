#!/bin/bash

openssl genrsa 1024 > rest.key
# openssl req -new -x509 -nodes -sha1 -days 365 -key rest.key > rest.cert
openssl req -new -x509 -nodes -sha1 -key rest.key > rest.cert
openssl x509 -in rest.cert -out rest.pem -outform PEM

