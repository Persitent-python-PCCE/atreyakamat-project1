pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                checkout scm
                apt install -y python3-pip
            }
        }
        stage('Installing Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                sh 'pytest'
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