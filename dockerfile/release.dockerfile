FROM python:3.6-alpine

LABEL maintainer="vapor@vapor.io"

# Environment variables for downloading the emulator plugin
ENV EMULATOR_REPO vapor-ware/synse-emulator-plugin
ENV EMULATOR_BIN  emulator_linux_amd64

# Environment variables for built-in emulator configuration.
ENV PLUGIN_DEVICE_CONFIG /synse/emulator/config
ENV PLUGIN_CONFIG /synse/emulator

COPY ./requirements.txt requirements.txt

# The linux_amd64 emulator binary is built with libc, not muslc, it
# will not work here. The musl and glibc so files are compatible, so
# we can make a symlink to fix the missing dependency:
# https://stackoverflow.com/a/35613430
RUN mkdir /lib64 && ln -s /lib/libc.musl-x86_64.so.1 /lib64/ld-linux-x86-64.so.2

RUN set -e -x \
    && apk --update --no-cache add \
        bash libstdc++ \
    && apk --update --no-cache --virtual .build-dep add \
        curl build-base jq \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && bin_url=$(curl -s https://api.github.com/repos/${EMULATOR_REPO}/releases/latest | jq '.assets[] | select(.name == env.EMULATOR_BIN) | .url' | tr -d '"') \
    && curl -L -H "Accept: application/octet-stream" -o $EMULATOR_BIN $bin_url \
    && chmod +x $EMULATOR_BIN \
    && mv $EMULATOR_BIN /usr/local/bin/emulator \
    && apk del .build-dep

COPY . /synse
WORKDIR /synse

# Create directories for plugin sockets and configuration
RUN mkdir -p /tmp/synse/procs \
    && mkdir -p /synse/config

# install synse_server python package
RUN python setup.py install

ENTRYPOINT ["bin/synse.sh"]
