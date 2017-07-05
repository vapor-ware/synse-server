FROM vaporio/vapor-endpoint-base-x64:1.0
MAINTAINER Erick Daniszewski <erick@vapor.io>

COPY requirements.txt /code/requirements.txt
COPY test-requirements.txt /code/test-requirements.txt

RUN pip install -r /code/test-requirements.txt

WORKDIR /code
