#!/usr/bin/env bash

# gencert.sh
#
# This script can be used to (re)generate the self-signed certs for the example deployment.
# Most of this was derived from: https://gist.github.com/fntlnz/cf14feb5a46b2eda428e000157447309

rootPrefix="certs/rootCA"
pluginPrefix="certs/emulator-plugin"
signingSubj="/C=US/ST=Texas/L=Austin/O=Vapor/CN=emulator-plugin"

# Create the root key
openssl genrsa -out "${rootPrefix}.key" 4096

# Create and self-sign the root certificate
openssl req -x509 -new -nodes -sha256 \
    -days 1024 \
    -subj "${signingSubj}" \
    -key "${rootPrefix}.key" \
    -out "${rootPrefix}.crt"

# Create the certificate key for the emulator plugin
openssl genrsa -out "${pluginPrefix}.key" 2048

# Create the signing (csr) for the emulator plugin
openssl req -new \
    -subj "${signingSubj}" \
    -key "${pluginPrefix}.key" \
    -out "${pluginPrefix}.csr"

# Generate the certificate for the emulator plugin
openssl x509 -req -sha256 \
    -in "${pluginPrefix}.csr" \
    -out "${pluginPrefix}.crt" \
    -CA "${rootPrefix}.crt" \
    -CAkey "${rootPrefix}.key" \
    -CAcreateserial \
    -days 500
