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

COPY . /synse
WORKDIR /synse

# Create directories for plugin sockets and configuration
RUN mkdir -p /tmp/synse/procs \
    && mkdir -p /synse/config

# install synse_server python package
RUN python setup.py install

ENTRYPOINT ["bin/synse.sh"]
