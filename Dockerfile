FROM resin/rpi-raspbian:wheezy
MAINTAINER Andrew Cencini <andrew@vapor.io>

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python \
    vim \
    nano \
    nginx \
    python-dev \
    python-pip \
    python-virtualenv \
    socat \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*
RUN pip install pyserial
RUN pip install flask
RUN pip install requests
RUN pip install uwsgi
# easy_install over pip for lockfile due to the fact that
# pip install lockfile is broken as of 8/3 on RPI
RUN easy_install lockfile
RUN mkdir /var/uwsgi
RUN chown www-data:www-data /var/uwsgi
RUN touch /var/uwsgi/reload
RUN usermod -a -G dialout www-data

# this should correspond to the opendcre dir
ADD . /opendcre
WORKDIR /opendcre

RUN ln -s /opendcre/opendcre_nginx.conf /etc/nginx/sites-enabled/nginx.conf

# expose our API endpoint port
EXPOSE 5000

# Define default command
CMD ["bash"]
