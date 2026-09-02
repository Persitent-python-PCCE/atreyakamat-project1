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
                sh 'docker build -t seatmeup:latest .'
            }
        }
        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials', 
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD')]) {
                            sh 'echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin'
                            sh 'docker tag seatmeup:latest atreya7/seatmeup:latest'
                            sh 'docker push atreya7/seatmeup:latest'
                }
            }
        }
    }
}