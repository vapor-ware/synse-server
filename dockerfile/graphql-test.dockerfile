FROM python:2.7-alpine
MAINTAINER Thomas Rampelberg <thomasr@vapor.io>

RUN mkdir /logs
COPY graphql/requirements.txt /graphql_frontend/requirements.txt
COPY graphql/testing-requirements.txt /graphql_frontend/testing-requirements.txt
RUN apk add --update alpine-sdk python-dev && \
  pip install -r /graphql_frontend/testing-requirements.txt
RUN pip install -r /graphql_frontend/requirements.txt

WORKDIR /graphql_frontend
CMD /bin/sh -c "while true; do sleep 100; done"
