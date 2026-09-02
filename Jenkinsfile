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
                    
                    if ! docker info > /dev/null 2>&1; then
                        echo "WARNING: Docker daemon is not accessible (unix:///var/run/docker.sock)."
                        echo "Skipping image build."
                        echo "true" > .skip_docker
                    else
                        docker build -t seatmeup:latest .
                        echo "false" > .skip_docker
                    fi
                '''
            }
        }
        stage('Push Docker Image') {
            steps {
                script {
                    try {
                        withCredentials([
                            usernamePassword(
                                credentialsId: 'dockerhub-credentials', 
                                usernameVariable: 'DOCKER_USERNAME',
                                passwordVariable: 'DOCKER_PASSWORD')]) {
                                    sh '''
                                        export PATH=$PATH:$HOME/.local/bin:$(pwd)/docker
                                        if [ -f .skip_docker ] && [ "$(cat .skip_docker)" = "true" ]; then
                                            echo "Skipping Docker Push because daemon is unavailable."
                                        else
                                            echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
                                            docker tag seatmeup:latest atreya7/seatmeup:latest
                                            docker push atreya7/seatmeup:latest
                                        fi
                                    '''
                        }
                    } catch (Exception e) {
                        echo "WARNING: Could not find credentials entry with ID 'dockerhub-credentials'. Skipping Docker Push."
                    }
                }
            }
        }
    }
}