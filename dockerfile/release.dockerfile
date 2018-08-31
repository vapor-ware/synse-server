#
# release.dockerfile
#
# The dockerfile for the default Synse Server release. This image
# contains Synse Server and a built-in plugin emulator. It is based
# off of the synse-server:base image (see slim.dockerfile), which
# installs the Synse Server dependencies, leaving this Dockerfile to
# only need to install the emulator.
#
# vaporio/synse-server:base is NOT in DockerHub, it is intended to be
# a local artifact from building slim.dockerfile. This way, this Dockerfile
# is not using outdated images as its base. This build artifact is created
# via the 'docker-slim' target.
#
# Note that because slim.dockerfile uses build args to set image metainfo,
# the build cache is invalidated so this image will always be rebuilt.
# The work done here should be minimal.
#
FROM vaporio/synse-server:base

# Set Image Metadata (mapping after dockerfile/slim.dockerfile).
ARG BUILD_DATE
ARG BUILD_VERSION
ARG VCS_REF

LABEL org.label-schema.schema-version="1.0" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="vaporio/synse-server" \
      org.label-schema.vcs-url="https://github.com/vapor-ware/synse-server" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vendor="Vapor IO" \
      org.label-schema.version=$BUILD_VERSION

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

