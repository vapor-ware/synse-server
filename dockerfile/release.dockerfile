FROM python:3.6-alpine
MAINTAINER Vapor IO <vapor@vapor.io>

ENV LANG en_US.utf8

# SYNSE_LANG determines the language to be used in logs and errors.
ENV SYNSE_LANG en_US

COPY ./requirements.txt requirements.txt

RUN set -e -x \
    && apk --update --no-cache add \
        bash gcc \
    && apk --update --no-cache --virtual .build-dep add \
        build-base \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apk del .build-dep

COPY . /synse
WORKDIR /synse

# FIXME -- this is temporary until I can figure out how to properly get this from GH
RUN pip3 install synse_plugin-*.tar.gz

# the location where the bg processes will place their
# unix sockets so the Synse app can communicate.
RUN mkdir -p /synse/procs

# install synse_server python package
# TODO - since we are pretty much just using the package, what
# if on build, we just pass in the tarball for synse_server.. then
# we don't have to also include the source code which isn't actually
# used (other than some of the configurations and runserver.py
RUN python setup.py install

ENTRYPOINT ["bin/synse.sh"]