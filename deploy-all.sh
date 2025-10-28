#!/bin/bash

# Complete deployment script for both backend and frontend

set -e  # Exit on error

echo "🚀 Complete Deployment: Backend + Frontend"
echo "=========================================="
echo ""

# Check for required environment variables
if [ -z "${GCP_PROJECT_ID}" ]; then
    echo "❌ Error: GCP_PROJECT_ID environment variable is required"
    echo ""
    echo "Usage:"
    echo "  export GCP_PROJECT_ID=your-project-id"
    echo "  export GCP_REGION=us-central1  # Optional, defaults to us-central1"
    echo "  ./deploy-all.sh"
    exit 1
fi

# Step 1: Deploy Backend
echo "Step 1/2: Deploying Backend..."
echo "=============================="
./deploy-backend.sh

# Get backend URL
BACKEND_SERVICE_URL=$(gcloud run services describe slimpai-backend --region ${GCP_REGION:-us-central1} --format 'value(status.url)')

echo ""
echo "✅ Backend deployed at: ${BACKEND_SERVICE_URL}"
echo ""

# Wait a bit for backend to be fully ready
echo "⏳ Waiting for backend to be ready..."
sleep 10

# Step 2: Deploy Frontend
echo ""
echo "Step 2/2: Deploying Frontend..."
echo "=============================="
export ADK_API_URL=${BACKEND_SERVICE_URL}
./deploy-frontend.sh

# Get frontend URL
FRONTEND_SERVICE_URL=$(gcloud run services describe slimpai-frontend --region ${GCP_REGION:-us-central1} --format 'value(status.url)')

echo ""
echo "🎉 Complete Deployment Successful!"
echo "=========================================="
echo ""
echo "📱 Your application is now live:"
echo "   Frontend: ${FRONTEND_SERVICE_URL}"
echo "   Backend:  ${BACKEND_SERVICE_URL}"
echo ""
echo "💡 Next steps:"
echo "1. Open the frontend URL in your browser"
echo "2. Start learning math with your AI assistant!"
echo ""
