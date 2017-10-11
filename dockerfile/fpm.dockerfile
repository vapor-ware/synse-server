FROM ruby:2.4.1-alpine

RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
RUN apk add --update alpine-sdk tar binutils rpm && \
  gem install fpm -v 1.8.1 && \
  apk del alpine-sdk

WORKDIR /data

ENTRYPOINT ["fpm"]
