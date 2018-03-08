FROM python:3.6-alpine
MAINTAINER Vapor IO <vapor@vapor.io>

COPY ./requirements.txt requirements.txt

RUN set -e -x \
    && apk --update --no-cache add \
        bash gcc curl \
    && apk --update --no-cache --virtual .build-dep add \
        build-base \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apk del .build-dep

COPY . /synse
WORKDIR /synse

# create directories for plugin sockets and configuration
RUN mkdir -p /tmp/synse/procs \
    && mkdir -p /synse/config

# install synse_server python package
# TODO - since we are pretty much just using the package, what
# if on build, we just pass in the tarball for synse_server.. then
# we don't have to also include the source code which isn't actually
# used (other than some of the configurations and runserver.py
RUN python setup.py install

ENTRYPOINT ["bin/synse.sh"]
