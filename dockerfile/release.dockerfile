FROM python:3.6-alpine
LABEL maintainer="vapor@vapor.io"

ARG BUILD_DATE
ARG BUILD_VERSION
ARG VCS_REF

# Environment variables for built-in emulator configuration.
ENV PLUGIN_DEVICE_CONFIG="/synse/emulator/config" \
    PLUGIN_CONFIG="/synse/emulator"

COPY requirements.txt requirements.txt
COPY bin/install_emulator.sh tmp/install_emulator.sh

# The linux_amd64 emulator binary is built with libc, not muslc, it
# will not work here. The musl and glibc so files are compatible, so
# we can make a symlink to fix the missing dependency:
# https://stackoverflow.com/a/35613430
RUN set -e -x \
    && mkdir /lib64 && ln -s /lib/libc.musl-x86_64.so.1 /lib64/ld-linux-x86-64.so.2 \
    && apk --update --no-cache add \
        bash libstdc++ \
    && apk --update --no-cache --virtual .build-dep add \
        curl build-base jq \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && EMULATOR_OUT=/usr/local/bin/emulator ./tmp/install_emulator.sh \
    && apk del .build-dep

# Image Metadata -- http://label-schema.org/rc1/
# This is set after the dependency install so we can cache that layer
LABEL org.label-schema.schema-version="1.0" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="vaporio/synse-server" \
      org.label-schema.vcs-url="https://github.com/vapor-ware/synse-server" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vendor="Vapor IO" \
      org.label-schema.version=$BUILD_VERSION

COPY . /synse
WORKDIR /synse

# Create directories for plugin sockets and configuration, then
# install Synse Server as a python package
RUN mkdir -p /tmp/synse/procs \
    && mkdir -p /synse/config \
    && python setup.py install

ENTRYPOINT ["bin/synse.sh"]
