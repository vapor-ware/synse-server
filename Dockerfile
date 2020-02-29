#
# BUILDER STAGE
#
FROM vaporio/python:3.8 as builder

COPY requirements.txt .

RUN pip install --prefix=/build -r /requirements.txt --no-warn-script-location \
 && rm -rf /root/.cache

COPY . /synse
RUN pip install --no-deps --prefix=/build --no-warn-script-location /synse \
 && rm -rf /root/.cache

#
# RELEASE STAGE
#
FROM vaporio/python:3.8-slim

LABEL maintainer="Vapor IO" \
      name="vaporio/synse-server" \
      url="https://github.com/vapor-ware/synse-server"

RUN groupadd -g 51453 synse \
 && useradd -u 51453 -g 51453 synse

RUN apt-get update && apt-get install -y --no-install-recommends \
    tini curl \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /etc/synse \
 && chown -R synse:synse /etc/synse

COPY --from=builder /build /usr/local
COPY ./assets/favicon.ico /etc/synse/static/favicon.ico

USER synse
ENTRYPOINT ["/usr/bin/tini", "--", "synse_server"]
