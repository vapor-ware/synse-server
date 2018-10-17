#
# release.dockerfile
#
# The Dockerfile for the release build of Synse Server. This
# Dockerfile has multiple stages:
#   * base: defines the base image and adds image metadata
#   * builder: build synse server package dependencies
#   * slim: a synse server build without emulator
#   * full: a synse server build with emulator
#

#
# BASE
#
FROM python:3.6-alpine as base
LABEL maintainer="Vapor IO"


#
# BUILDER
#
FROM python:3.6-alpine as builder

RUN mkdir /build
WORKDIR /build

COPY requirements.txt /requirements.txt

RUN set -e -x \
    && apk --update --no-cache --virtual .build-dep add \
        build-base \
    && pip install --upgrade pip \
    && pip install --prefix=/build -r /requirements.txt --no-warn-script-location \
    && rm -rf /root/.cache \
    && apk del .build-dep


#
# SLIM
#
FROM base as slim
COPY --from=builder /build /usr/local

RUN set -e -x \
    && apk --update --no-cache add \
        bash libstdc++ ca-certificates tini

# Set image metadata (see: http://label-schema.org/rc1/)
ARG BUILD_VERSION
ARG BUILD_DATE
ARG VCS_REF

LABEL org.label-schema.schema-version="1.0" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="vaporio/synse-server" \
      org.label-schema.vcs-url="https://github.com/vapor-ware/synse-server" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vendor="Vapor IO" \
      org.label-schema.version=$BUILD_VERSION

COPY . /synse
WORKDIR /synse

RUN pip uninstall -y synse-grpc && \
    pip install synse_grpc-1.1.0.tar.gz

# Create directories for plugin sockets and configuration, then
# install Synse Server as a python package
RUN mkdir -p /tmp/synse/procs \
    && mkdir -p /synse/config \
    && pip install . \
    && rm -rf /root/.cache

ENTRYPOINT ["/sbin/tini", "--", "bin/synse.sh"]


#
# FULL
#
FROM slim as full

# Emulator installation script
COPY bin/install_emulator.sh tmp/install_emulator.sh

# Environment variables for built-in emulator configuration.
ENV PLUGIN_DEVICE_CONFIG="/synse/emulator/config/device" \
    PLUGIN_CONFIG="/synse/emulator"

# The linux_amd64 emulator binary is built with libc, not muslc, it
# will not work here. The musl and glibc so files are compatible, so
# we can make a symlink to fix the missing dependency:
# https://stackoverflow.com/a/35613430
RUN set -e -x \
    && mkdir /lib64 && ln -s /lib/libc.musl-x86_64.so.1 /lib64/ld-linux-x86-64.so.2 \
    && apk --update --no-cache --virtual .build-dep add \
        curl jq \
    && EMULATOR_OUT=/usr/local/bin/emulator ./tmp/install_emulator.sh \
    && apk del .build-dep
