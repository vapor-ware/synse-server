#!/usr/bin/env bash

VERSION_SENTINEL="SYNSE_VERSION"
SYNSE_VERSION="1.3"

sed -i -e "s/$VERSION_SENTINEL/$SYNSE_VERSION/g" synse_nginx.conf