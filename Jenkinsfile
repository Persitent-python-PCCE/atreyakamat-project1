pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                checkout scm
            }
        }
        stage('Installing Dependencies') {
            steps {
                sh '''
                    export PATH=$PATH:$HOME/.local/bin
                    pip install --break-system-packages -r requirements.txt
                    pip install --break-system-packages pytest
                '''
            }
        }
        stage('Test') {
            steps {
                sh '''
                    export PATH=$PATH:$HOME/.local/bin
                    python3 -m pytest || pytest
                '''
            }
        }
        stage('Build Docker Image') {
            steps {
                sh '''
                    export PATH=$PATH:$HOME/.local/bin:$(pwd)/docker
                    if ! command -v docker &> /dev/null; then
                        echo "Docker CLI not found. Downloading statically..."
                        curl -fsSLO https://download.docker.com/linux/static/stable/x86_64/docker-24.0.9.tgz
                        tar xzvf docker-24.0.9.tgz
                    fi
                    docker build -t seatmeup:latest .
                '''
            }
        }
        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials', 
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD')]) {
                            sh '''
                                export PATH=$PATH:$HOME/.local/bin:$(pwd)/docker
                                echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
                                docker tag seatmeup:latest atreya7/seatmeup:latest
                                docker push atreya7/seatmeup:latest
                            '''
                }
            }
        }
    }
}