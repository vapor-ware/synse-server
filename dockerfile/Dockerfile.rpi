FROM resin/rpi-raspbian:jessie
MAINTAINER Andrew Cencini <andrew@vapor.io>

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python \
    vim \
    nano \
    nginx \
    python-setuptools \
    python-dev \
    python-pip \
    python-virtualenv \
    socat \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*
RUN pip install pyserial==2.7 flask
RUN pip install -I requests==2.9.1
RUN pip install uwsgi RPi.GPIO docker-py pymongo pyghmi
# easy_install over pip for lockfile due to the fact that
# pip install lockfile is broken as of 8/3/15 on RPI
RUN easy_install lockfile
RUN mkdir /var/uwsgi
RUN chown www-data:www-data /var/uwsgi
RUN touch /var/uwsgi/reload
RUN usermod -a -G dialout www-data

# this should correspond to the opendcre/southbound-api dir
ADD . /opendcre
WORKDIR /opendcre

# link in the appropriate config file, based on ssl_enable flag
RUN ./nginx-conf.sh

# set up SSL support for nginx
ADD ./certs/southbound_rpi /etc/nginx/ssl

# expose our API endpoint port
EXPOSE 5000

# Define default command
CMD ["./start_opendcre.sh"]
