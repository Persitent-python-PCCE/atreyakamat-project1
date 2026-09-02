#!/bin/bash
if ! command -v docker &> /dev/null; then
    echo "Docker CLI not found. Downloading static binary..."
    curl -fsSLO https://download.docker.com/linux/static/stable/x86_64/docker-24.0.9.tgz
    tar xzvf docker-24.0.9.tgz
    mkdir -p $HOME/.local/bin
    cp docker/docker $HOME/.local/bin/
    chmod +x $HOME/.local/bin/docker
    rm -rf docker docker-*.tgz
fi
