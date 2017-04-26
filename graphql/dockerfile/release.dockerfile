FROM python:3.6-alpine
MAINTAINER Thomas Rampelberg <thomasr@vapor.io>

RUN mkdir /logs
# Run the dependencies as a single layer
COPY requirements.txt /graphql_frontend/requirements.txt
RUN pip install -r /graphql_frontend/requirements.txt

COPY . /graphql_frontend

WORKDIR /graphql_frontend
CMD python runserver.py
