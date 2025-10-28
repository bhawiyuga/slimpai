#!/bin/bash

# Deployment script for Streamlit Frontend to Google Cloud Run

set -e  # Exit on error

# Configuration
PROJECT_ID="qwiklabs-gcp-03-79ce60c107d6"
REGION="us-central1"
SERVICE_NAME="slimpai-frontend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
BACKEND_URL="${ADK_API_URL}"

echo "🚀 Deploying Streamlit Frontend to Google Cloud Run"
echo "===================================================="
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service Name: ${SERVICE_NAME}"
echo "Backend URL: ${BACKEND_URL}"
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

# Check if backend URL is set
if [ -z "${BACKEND_URL}" ]; then
    echo "⚠️  Warning: ADK_API_URL not set"
    echo "The frontend won't be able to connect to the backend"
    echo "Set it with: export ADK_API_URL=https://your-backend-url"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    BACKEND_URL="http://localhost:8000"
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
cat > /tmp/cloudbuild-frontend.yaml <<EOF
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', '${IMAGE_NAME}', '-f', 'Dockerfile.frontend', '.']
images: ['${IMAGE_NAME}']
EOF

gcloud builds submit --config=/tmp/cloudbuild-frontend.yaml .

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
    --set-env-vars "ADK_API_URL=${BACKEND_URL},PYTHONUNBUFFERED=1" \
    --max-instances 10 \
    --min-instances 0

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo ""
echo "✅ Frontend deployment complete!"
echo "===================================================="
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "💡 You can now access your Math Learning Assistant at:"
echo "   ${SERVICE_URL}"
echo ""
