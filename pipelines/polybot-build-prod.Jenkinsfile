pipeline {
    agent {
        label 'general'  // or 'any' or your specific agent name
    }

    triggers {
        githubPush() // makes it run on push
    }

    environment {
        // Docker credentials from Jenkins Credentials Manager
       DOCKER_USERNAME = credentials('dockerhub-username') // ID from Jenkins credentials
       DOCKER_PASSWORD = credentials('dockerhub-token')     // ID from Jenkins credentials
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Docker Login') {
            steps {
                sh '''
                    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
                '''
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                script {
                    def imageTag = "${DOCKER_USERNAME}/polybot-prod:${BUILD_NUMBER}"
                    env.IMAGE_TAG = imageTag

                    sh """
                        docker build -t ${IMAGE_TAG} .
                        docker push ${IMAGE_TAG}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ Docker image pushed: ${env.IMAGE_TAG}"
        }
        failure {
            echo "❌ Build failed"
        }
    }
}
