# Builds the Synse Server production release image.
FROM ubuntu:16.04
MAINTAINER Vapor IO <eng@vapor.io>

COPY ./requirements.txt requirements.txt

RUN set -ex \
    && buildDeps='python-dev python-pip unzip make swig build-essential' \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        curl libftdi-dev libpython2.7 python snmp socat $buildDeps \
    && curl -O https://nginx.org/keys/nginx_signing.key && apt-key add ./nginx_signing.key \
    && echo "deb http://nginx.org/packages/ubuntu/ xenial nginx" >> /etc/apt/sources.list \
    && echo "deb-src http://nginx.org/packages/ubuntu/ xenial nginx" >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y nginx \
    && pip install --upgrade pip setuptools \
    && pip install -r requirements.txt \
    && pip install uwsgi \
    && curl -LOk https://github.com/devttys0/libmpsse/archive/master.zip \
    && unzip master.zip && rm master.zip \
    && cd libmpsse-master/src \
    && ./configure && make && make install \
    && pip uninstall -y setuptools \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove $buildDeps \
    && apt-get autoremove -y \
    && apt-get clean

ADD . /synse
WORKDIR /synse

# update the python path to include the synse module so that it
# can be successfully be imported
ENV PYTHONPATH="/synse/synse:${PYTHONPATH}"

RUN mkdir -p /etc/uwsgi \
    && touch /etc/uwsgi/reload \
    && ln -s /synse/configs/uwsgi/synse.ini /etc/uwsgi/synse.ini \
    && chown -R www-data:www-data /etc/uwsgi \
    && ln -s /synse/configs/nginx/nginx.conf /etc/nginx/conf.d/nginx.conf \
    && ln -sf /proc/1/fd/1 /var/log/nginx/access.log \
    && ln -sf /proc/1/fd/2 /var/log/nginx/error.log \
    && sed -i -e "s/VERSION_SENTINEL/$(python synse/version.py api)/g" /synse/configs/nginx/nginx.conf \
    && mkdir /logs \
    && chown :www-data /logs \
    && chmod 775 /logs

# Expose our API endpoint port.
EXPOSE 5000

ENTRYPOINT ["/synse/bin/synse.sh"]
