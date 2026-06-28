# Newbie Cloud Agent base image — system deps for cloud_bootstrap.sh.
# Cursor checks out the repo; do not COPY the project into this image.
FROM ubuntu:24.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    sudo \
    python3 \
    python3-pip \
    python3-venv \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
