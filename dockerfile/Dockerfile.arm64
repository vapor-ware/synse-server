FROM vaporio/debian-jessie-arm64
MAINTAINER Andrew Cencini <andrew@vapor.io>

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    make \
    python \
    vim \
    nano \
    nginx \
    python-dev \
    python-pip \
    python-setuptools \
    python-virtualenv \
    pyghmi \
    socat \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*
RUN pip install pyserial
RUN pip install flask
RUN pip install -I requests==2.9.1
#RUN pip install docker-py
#RUN pip install pymongo
RUN mkdir /usr/lib/uwsgi && \
    git clone https://github.com/unbit/uwsgi.git && \
    cd uwsgi && \
    git checkout uwsgi-2.0 && \
    make clean && \
    echo "plugin_dir = /usr/lib/uwsgi" >> buildconf/opendcre.ini && \
    UWSGI_PROFILE=opendcre make && \
    cp uwsgi /usr/local/bin && \
    python uwsgiconfig.py --plugin plugins/python opendcre
#RUN pip install uwsgi
# easy_install over pip for lockfile due to the fact that
# pip install lockfile is broken as of 8/3 on RPI
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
ADD ./certs/southbound_arm64 /etc/nginx/ssl

# expose our API endpoint port
EXPOSE 5000

# Define default command
CMD ["./start_opendcre.sh"]
