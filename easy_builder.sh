#!/bin/bash
set -e

echo "=== Easy Builder ==="
echo "1. Installing dependencies..."
pip install --break-system-packages -r requirements.txt
pip install --break-system-packages pytest

echo "2. Running Tests..."
python3 -m pytest || pytest

echo "3. Checking Docker CLI..."
if ! command -v docker &> /dev/null; then
    echo "Docker CLI not found. Downloading statically..."
    curl -fsSLO https://download.docker.com/linux/static/stable/x86_64/docker-24.0.9.tgz
    tar xzvf docker-24.0.9.tgz
    export PATH=$PATH:$(pwd)/docker
fi

echo "4. Building Docker Image..."
docker build -t seatmeup:latest .

if [ -n "$DOCKER_USERNAME" ] && [ -n "$DOCKER_PASSWORD" ]; then
    echo "5. Pushing Docker Image..."
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
    docker tag seatmeup:latest atreya7/seatmeup:latest
    docker push atreya7/seatmeup:latest
else
    echo "Skipping push (DOCKER_USERNAME and DOCKER_PASSWORD not set)."
fi

echo "=== Build Complete ==="
