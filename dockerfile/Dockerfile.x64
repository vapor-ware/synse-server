FROM vaporio/vapor-endpoint-base-x64:1.0
MAINTAINER Andrew Cencini <andrew@vapor.io>

ENV VAPOR_SERVICE_NAME=opendcre

# Install dependencies
RUN apt-get update && apt-get install -y \
    socat \
    python-dev \
    make \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* && \
    pip install pyserial==2.7 \
    RPi.GPIO \
    pyghmi \
    grequests

RUN mkdir /var/uwsgi && \
    chown www-data:www-data /var/uwsgi && \
    touch /var/uwsgi/reload

# this should correspond to the opendcre/southbound-api dir
ADD . /opendcre
WORKDIR /opendcre

# run command for nginx configuration
RUN ln -s /opendcre/opendcre_nginx.conf /etc/nginx/sites-enabled/nginx.conf && \
    rm -f /etc/logrotate.d/nginx && \
    cp /opendcre/configs/nginx.logrotate /etc/logrotate.d/nginx && \
    ln -sf /proc/1/fd/1 /logs/err

# update the python path to include the opendcre southbound module so that it
# can be successfully be imported
ENV PYTHONPATH="/opendcre/opendcre_southbound:${PYTHONPATH}"

# Expose our API endpoint port.
EXPOSE 5000

# Define default command
CMD ["./start_opendcre.sh"]
