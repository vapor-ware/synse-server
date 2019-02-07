#
# synse.dockerfile
#
# The Dockerfile for the release build of Synse Server. This
# Dockerfile has multiple stages:
#   * builder: build synse server package dependencies
#   * slim: a synse server build without emulator
#   * full: a synse server build with emulator
#

#
# BUILDER
#
FROM vaporio/python:3.6 as builder
COPY requirements.txt .

# FIXME: protobuf should be removed here, it should be a dep of synse_grpc
RUN pip install --prefix=/build -r /requirements.txt --no-warn-script-location protobuf \
 && rm -rf /root/.cache

COPY . /synse
RUN pip install --no-deps --prefix=/build --no-warn-script-location /synse \
 && rm -rf /root/.cache

#
# SLIM
#
FROM vaporio/python:3.6-slim as slim

RUN apt-get update && apt-get install -y --no-install-recommends tini \
 && rm -rf /var/lib/apt/lists/*

LABEL maintainer="Vapor IO" \
      name="vaporio/synse-server" \
      url="https://github.com/vapor-ware/synse-server"

# Create directories for plugin sockets and configuration, then
# install Synse Server as a python package
# TODO: this will eventually be done via synse-server itself..
RUN mkdir -p /tmp/synse/procs \
 && mkdir -p /synse/config

COPY --from=builder /build /usr/local

ENTRYPOINT ["/usr/bin/tini", "--", "synse-server"]


#
# FULL
#
FROM slim as full

# Environment variables for built-in emulator configuration.
ENV PLUGIN_DEVICE_CONFIG="/synse/emulator/config/device" \
    PLUGIN_CONFIG="/synse/emulator"

COPY emulator /synse/emulator
COPY bin/install_emulator.sh /tmp/install_emulator.sh

RUN apt-get update \
 && apt-get install --no-install-recommends -y jq curl \
 && EMULATOR_OUT=/usr/local/bin/synse-emulator /tmp/install_emulator.sh \
 && apt-get purge -y jq curl \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*
