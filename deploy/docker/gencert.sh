#!/usr/bin/env bash

#openssl req \
#  -new \
#  -newkey rsa:4096 \
#  -days 3650 \
#  -nodes \
#  -x509 \
#  -subj "/C=US/ST=Texas/L=Austin/O=Vapor/CN=localhost" \
#  -keyout emulator-plugin.key \
#  -out emulator-plugin.cert

openssl genrsa -out rootCA.key 4096
openssl req -x509 -subj "/C=US/ST=Texas/L=Austin/O=Vapor/CN=emulator-plugin" -new -nodes -key rootCA.key -sha256 -days 1024 -out rootCA.crt
openssl genrsa -out emulator-plugin.key 2048
openssl req -new -key emulator-plugin.key -out emulator-plugin.csr -subj "/C=US/ST=Texas/L=Austin/O=Vapor/CN=emulator-plugin"
openssl x509 -req -in emulator-plugin.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out emulator-plugin.crt -days 500 -sha256