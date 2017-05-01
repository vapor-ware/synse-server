FROM python:3.6-alpine
MAINTAINER Thomas Rampelberg <thomasr@vapor.io>

RUN mkdir /logs
COPY requirements.txt /graphql_frontend/requirements.txt
COPY testing-requirements.txt /graphql_frontend/testing-requirements.txt
RUN apk add --update alpine-sdk python3-dev && \
  pip install -r /graphql_frontend/testing-requirements.txt && \
  pip install -r /graphql_frontend/requirements.txt

WORKDIR /graphql_frontend
CMD /bin/sh -c "while true; do sleep 100; done"
