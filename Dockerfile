#
# BUILDER STAGE
#
FROM vaporio/python:3.6 as builder

COPY requirements.txt .

RUN pip install --prefix=/build -r /requirements.txt --no-warn-script-location \
 && rm -rf /root/.cache

COPY . /synse
RUN pip install --no-deps --prefix=/build --no-warn-script-location /synse \
 && rm -rf /root/.cache

#
# RELEASE STAGE
#
FROM vaporio/python:3.6-slim

LABEL maintainer="Vapor IO" \
      name="vaporio/synse-server" \
      url="https://github.com/vapor-ware/synse-server"

RUN apt-get update && apt-get install -y --no-install-recommends \
    tini curl \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build /usr/local
COPY ./assets/favicon.ico /etc/synse/static/favicon.ico

ENTRYPOINT ["/usr/bin/tini", "--", "synse_server"]
