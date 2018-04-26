FROM python:3.6-alpine
LABEL maintainer="vapor@vapor.io"

COPY requirements.txt requirements.txt

RUN set -e -x \
    && apk --update --no-cache add \
        bash libstdc++ \
    && apk --update --no-cache --virtual .build-dep add \
        build-base \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apk del .build-dep

# Image Metadata -- http://label-schema.org/rc1/
# This is set after the dependency install so we can cache that layer
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

COPY . /synse
WORKDIR /synse

# Create directories for plugin sockets and configuration, then
# install Synse Server as a python package
RUN mkdir -p /tmp/synse/procs \
    && mkdir -p /synse/config \
    && python setup.py install

ENTRYPOINT ["bin/synse.sh"]
