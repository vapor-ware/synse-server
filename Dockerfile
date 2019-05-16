#
# BUILDER STAGE
#
FROM vaporio/python:3.6 as builder

COPY requirements.txt .

# FIXME: this should be removed once synse-grpc 3.0.0 is released
COPY synse_grpc-3.0.0.tar.gz .
RUN pip install --prefix=/build --no-warn-script-location synse_grpc-3.0.0.tar.gz \
 && rm -rf /root/.cache

RUN pip install --prefix=/build -r /requirements.txt --no-warn-script-location \
 && rm -rf /root/.cache

COPY . /synse
RUN pip install --no-deps --prefix=/build --no-warn-script-location /synse \
 && rm -rf /root/.cache

#
# RELEASE STAGE
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

# FIXME: this should be removed once synse-grpc 3.0.0 is released
COPY synse_grpc-3.0.0.tar.gz .
RUN pip install synse_grpc-3.0.0.tar.gz

ENTRYPOINT ["/usr/bin/tini", "--", "synse_server"]
