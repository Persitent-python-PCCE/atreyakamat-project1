#!/bin/bash
set -e

echo "=== Easy Builder ==="
echo "1. Installing dependencies..."
if ! python3 -c "import pip" &> /dev/null; then
    echo "pip not found. Installing via get-pip.py..."
    curl -fsSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --break-system-packages
fi
python3 -m pip install --break-system-packages -r requirements.txt
python3 -m pip install --break-system-packages pytest

echo "2. Running Tests..."
python3 -m pytest || pytest

echo "3. Checking Docker CLI..."
if ! command -v docker &> /dev/null; then
    echo "Docker CLI not found. Downloading statically..."
    curl -fsSLO https://download.docker.com/linux/static/stable/x86_64/docker-24.0.9.tgz
    tar xzvf docker-24.0.9.tgz
    export PATH=$PATH:$(pwd)/docker
fi

echo "4. Checking Docker Daemon..."
if ! docker info > /dev/null 2>&1; then
    echo "WARNING: Docker daemon is not accessible. Skipping image build and push."
else
    echo "5. Building Docker Image..."
    docker build -t seatmeup:latest .

    if [ -n "$DOCKER_USERNAME" ] && [ -n "$DOCKER_PASSWORD" ]; then
        echo "6. Pushing Docker Image..."
        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
        docker tag seatmeup:latest atreya7/seatmeup:latest
        docker push atreya7/seatmeup:latest
    else
        echo "Skipping push (DOCKER_USERNAME and DOCKER_PASSWORD not set)."
    fi
fi

echo "=== Build Complete ==="
