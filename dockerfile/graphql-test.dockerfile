FROM python:2.7-alpine
MAINTAINER Thomas Rampelberg <thomasr@vapor.io>

RUN mkdir /logs

COPY requirements.txt /synse/requirements.txt
COPY test-requirements.txt /synse/test-requirements.txt

RUN apk add --update alpine-sdk python-dev \
    && pip install -r /synse/test-requirements.txt

WORKDIR /synse
CMD /bin/sh -c "while true; do sleep 100; done"
