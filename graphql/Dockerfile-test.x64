FROM python:3.6-alpine
MAINTAINER Thomas Rampelberg <thomasr@vapor.io>

# This needs to be a copy of Dockerfile.x64 because of how layers and dependent containers work.
RUN mkdir /logs
COPY requirements.txt /graphql_frontend/requirements.txt
COPY testing-requirements.txt /graphql_frontend/testing-requirements.txt
RUN apk add --update alpine-sdk python3-dev && \
  pip install -r /graphql_frontend/testing-requirements.txt && \
  pip install -r /graphql_frontend/requirements.txt

WORKDIR /graphql_frontend
CMD /bin/sh
