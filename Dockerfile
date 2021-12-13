#
# BUILDER STAGE
#
FROM docker.io/vaporio/python:3.9 as builder

RUN pip install --disable-pip-version-check poetry

WORKDIR /build
COPY . .

RUN poetry export --without-hashes -f requirements.txt > requirements.txt \
 && poetry build -f sdist

RUN mkdir packages \
 && pip download \
      -r requirements.txt \
      -d packages \
      --disable-pip-version-check

#
# RELEASE STAGE
#
FROM docker.io/vaporio/python:3.9-slim

LABEL org.opencontainers.image.title="Synse Server" \
      org.opencontainers.image.source="https://github.com/vapor-ware/synse-server" \
      org.opencontainers.image.url="https://github.com/vapor-ware/synse-server" \
      org.opencontainers.image.vendor="Vapor IO" \
      org.opencontainers.image.authors="erick@vapor.io"

RUN groupadd -g 51453 synse \
 && useradd -u 51453 -g 51453 synse

RUN apt-get update && apt-get install -y --no-install-recommends \
    tini curl \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /synse \
 && mkdir -p /etc/synse \
 && chown -R synse:synse /synse \
 && chown -R synse:synse /etc/synse

COPY --from=builder /build/dist/synse-server-*.tar.gz /synse/synse-server.tar.gz
COPY --from=builder /build/packages /pip-packages
COPY ./assets/favicon.ico /etc/synse/static/favicon.ico

WORKDIR synse

RUN pip install --no-index --find-links=/pip-packages /pip-packages/* \
 && pip install synse-server.tar.gz \
 && rm -rf /root/.cache

USER synse

ENTRYPOINT ["/usr/bin/tini", "--", "synse_server"]
