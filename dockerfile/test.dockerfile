FROM python:3.6-alpine
MAINTAINER Vapor IO <vapor@vapor.io>

ENV LANG en_US.utf8

RUN apk add --update \
  alpine-sdk \
  bash

RUN pip install --upgrade pip setuptools
RUN pip install tox

WORKDIR /code

COPY synse_plugin-*.tar.gz .

CMD ["bin/run_tests.sh"]