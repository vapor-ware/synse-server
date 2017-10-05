# Builds an image used for running tests out of.
FROM vaporio/vapor-endpoint-base-x64:1.0
MAINTAINER Vapor IO <eng@vapor.io>

COPY requirements.txt /code/requirements.txt
COPY test-requirements.txt /code/test-requirements.txt

RUN pip install -r /code/test-requirements.txt

WORKDIR /code
