#!/usr/bin/env bash

openssl req \
  -new \
  -newkey rsa:4096 \
  -days 3650 \
  -nodes \
  -x509 \
  -subj "/C=US/ST=Texas/L=Austin/O=Vapor/CN=localhost" \
  -keyout emulator-plugin.key \
  -out emulator-plugin.cert