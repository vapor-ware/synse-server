# Used to create a release in GitHub and upload it.
FROM debian:jessie-slim

RUN apt-get update && apt-get install -y \
  git && \
  rm -rf /var/lib/apt/lists/*

ADD https://github.com/github/hub/releases/download/v2.3.0-pre9/hub-linux-amd64-2.3.0-pre9.tgz /tmp
RUN cd /tmp && tar xzf /tmp/*.tgz && /bin/bash /tmp/hub*/install

WORKDIR /data

ENTRYPOINT ["/usr/local/bin/hub"]
