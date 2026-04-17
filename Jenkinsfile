pipeline {
    agent any

    environment {
        REPO_URL = "https://github.com/VashuTheGreat/JOSAA_RANK_PREDICTOR.git"
        PROJECT_NAME = "JOSAA_RANK_PREDICTOR"
        HF_TOKEN = credentials('HF_TOKEN')

    }

    stages {

        stage('Clone Repository') {
            steps {
                echo "📥 Cloning repository..."
                git branch: 'main', url: "${REPO_URL}"
            }
        }

        stage('Give Permission') {
            steps {
                echo "🔐 Giving execute permission to script..."
                sh 'chmod +x deploye.sh'
            }
        }

        stage('Run Deployment Script') {
            steps {
                echo "🚀 Running deployment script..."
                sh './deploye.sh'
            }
        }

    }

    post {
        success {
            echo "✅ Pipeline executed successfully!"
        }
        failure {
            echo "❌ Pipeline failed!"
        }
    }
}