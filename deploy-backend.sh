#!/bin/bash

# Deployment script for ADK API Backend to Google Cloud Run

set -e  # Exit on error

# Configuration
PROJECT_ID="qwiklabs-gcp-03-79ce60c107d6"
REGION="us-central1"
SERVICE_NAME="slimpai-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying ADK API Backend to Google Cloud Run"
echo "=================================================="
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service Name: ${SERVICE_NAME}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if project ID is set
if [ "${PROJECT_ID}" = "your-project-id" ]; then
    echo "❌ Error: Please set GCP_PROJECT_ID environment variable"
    echo "Example: export GCP_PROJECT_ID=my-project-123"
    exit 1
fi

# Set the project
echo "📋 Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build the Docker image
echo "🏗️  Building Docker image..."
cat > /tmp/cloudbuild-backend.yaml <<EOF
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', '${IMAGE_NAME}', '-f', 'Dockerfile.backend', '.']
images: ['${IMAGE_NAME}']
EOF

gcloud builds submit --config=/tmp/cloudbuild-backend.yaml .

# Deploy to Cloud Run
echo "🚢 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --set-env-vars "PYTHONUNBUFFERED=1" \
    --max-instances 10 \
    --min-instances 0

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo ""
echo "✅ Backend deployment complete!"
echo "=================================================="
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "💡 Next steps:"
echo "1. Test the backend: curl ${SERVICE_URL}/health"
echo "2. Use this URL as ADK_API_URL when deploying frontend"
echo "3. Deploy frontend: export ADK_API_URL=${SERVICE_URL} && ./deploy-frontend.sh"
echo ""
