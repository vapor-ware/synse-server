#!/bin/bash

SSL_ENABLE=$(awk -F "[:,]" '/ssl_enable/ {print $2}' opendcre_config.json)
echo ${SSL_ENABLE}

if [ ${SSL_ENABLE} = "true" ]
then
    ln -s /opendcre/opendcre_ssl_nginx.conf /etc/nginx/sites-enabled/nginx.conf
else
    ln -s /opendcre/opendcre_nginx.conf /etc/nginx/sites-enabled/nginx.conf
fi