FROM ruby:2.5-alpine

RUN apk add --update --no-cache \
        coreutils git make g++ nodejs

RUN git clone https://github.com/lord/slate && mv /slate/source /slate/tmp

WORKDIR /slate
RUN bundle install

VOLUME /source
VOLUME /build

CMD cp -r /source source && cp -nr tmp/* source && exec bundle exec middleman build