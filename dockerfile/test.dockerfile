FROM python:3.6-alpine
MAINTAINER Vapor IO <vapor@vapor.io>

RUN apk add --update \
  alpine-sdk \
  bash

RUN pip install --upgrade pip setuptools
RUN pip install tox

WORKDIR /code

ENTRYPOINT ["bin/run_tests.sh"]
