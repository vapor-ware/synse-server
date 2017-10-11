FROM ruby:2.4-alpine

RUN gem install package_cloud -v 0.2.42

ENTRYPOINT ["package_cloud"]
