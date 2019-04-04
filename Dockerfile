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
COPY synse_grpc-3.0.0.tar.gz .

RUN pip install --prefix=/build --no-warn-script-location synse_grpc-3.0.0.tar.gz \
 && rm -rf /root/.cache

RUN pip install --prefix=/build -r /requirements.txt --no-warn-script-location \
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
 && mkdir -p /synse/config \
 && mkdir -p /etc/synse/static

COPY --from=builder /build /usr/local
COPY ./assets/favicon.ico /etc/synse/static/favicon.ico

ENTRYPOINT ["/usr/bin/tini", "--", "synse-server"]


#
# FULL
#
FROM slim as full

# Environment variables for built-in emulator configuration and
# installation from GitHub release.
ENV PLUGIN_DEVICE_CONFIG="/synse/emulator/config/device" \
    PLUGIN_CONFIG="/synse/emulator" \
    EMULATOR_VERSION="2.3.1"

# Install the specified version of the emulator.
RUN apt-get update \
 && apt-get install --no-install-recommends -y curl \
 && curl -L \
    -H "Accept: application/octet-stream" \
    -o /usr/local/bin/synse-emulator \
    https://github.com/vapor-ware/synse-emulator-plugin/releases/download/${EMULATOR_VERSION}/emulator_linux_amd64 \
 && chmod +x /usr/local/bin/synse-emulator \
 && apt-get purge -y curl \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

# Copy in the emulator configurations.
COPY emulator /synse/emulator
