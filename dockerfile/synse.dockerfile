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

RUN pip install --prefix=/build -r /requirements.txt --no-warn-script-location

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

COPY --from=builder /build /usr/local
#COPY . /synse
#
#WORKDIR /synse

#COPY . /synse
#WORKDIR /synse

# Create directories for plugin sockets and configuration, then
# install Synse Server as a python package
# TODO: this will eventually be done via synse-server itself..
RUN mkdir -p /tmp/synse/procs \
 && mkdir -p /synse/config
# && pip install . \
# && rm -rf /root/.cache
#
## Set image metadata (see: http://label-schema.org/rc1/)
#ARG BUILD_VERSION
#ARG BUILD_DATE
#ARG VCS_REF
#
#LABEL maintainer="Vapor IO"\
#      org.label-schema.schema-version="1.0" \
#      org.label-schema.build-date=$BUILD_DATE \
#      org.label-schema.name="vaporio/synse-server" \
#      org.label-schema.vcs-url="https://github.com/vapor-ware/synse-server" \
#      org.label-schema.vcs-ref=$VCS_REF \
#      org.label-schema.vendor="Vapor IO" \
#      org.label-schema.version=$BUILD_VERSION

#COPY --from=builder /build /usr/local

ENTRYPOINT ["/usr/bin/tini", "--", "synse-server"]


#
# FULL
#
FROM slim as full

# Environment variables for built-in emulator configuration.
ENV PLUGIN_DEVICE_CONFIG="/synse/emulator/config/device" \
    PLUGIN_CONFIG="/synse/emulator"

COPY bin/install_emulator.sh /tmp/install_emulator.sh

RUN apt-get update \
 && apt-get install --no-install-recommends -y jq curl \
 && EMULATOR_OUT=/usr/local/bin/synse-emulator /tmp/install_emulator.sh \
 && apt-get purge -y jq curl \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*
