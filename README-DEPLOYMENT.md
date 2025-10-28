# Deployment Guide for SLIMPai on Google Cloud Run

This guide explains how to deploy the Math Learning Assistant application (frontend and backend) to Google Cloud Run.

## Architecture

- **Backend**: Google ADK API Server (Python)
- **Frontend**: Streamlit Web Application (Python)
- **Platform**: Google Cloud Run (serverless containers)

## Prerequisites

1. **Google Cloud Account**: You need a GCP account with billing enabled
2. **gcloud CLI**: Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
3. **Project Setup**: Create a GCP project or use an existing one

## Initial Setup

### 1. Install and Configure gcloud

```bash
# Install gcloud (if not already installed)
# Follow: https://cloud.google.com/sdk/docs/install

# Login to your Google account
gcloud auth login

# Set your project ID
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID

# Optional: Set your preferred region
export GCP_REGION="us-central1"  # or your preferred region
```

### 2. Enable Required APIs

The deployment scripts will automatically enable these, but you can do it manually:

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## Deployment Options

### Option 1: Deploy Everything at Once (Recommended)

This is the simplest approach - it deploys both backend and frontend in sequence:

```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"

# Optional: Set region (defaults to us-central1)
export GCP_REGION="us-central1"

# Make the script executable
chmod +x deploy-all.sh

# Deploy both backend and frontend
./deploy-all.sh
```

### Option 2: Deploy Backend and Frontend Separately

If you want more control, deploy each service individually:

#### Deploy Backend First

```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"

chmod +x deploy-backend.sh
./deploy-backend.sh
```

This will output the backend URL, for example:
```
Service URL: https://slimpai-backend-xxxxx-uc.a.run.app
```

#### Deploy Frontend

```bash
# Use the backend URL from the previous step
export ADK_API_URL="https://slimpai-backend-xxxxx-uc.a.run.app"
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"

chmod +x deploy-frontend.sh
./deploy-frontend.sh
```

### Option 3: CI/CD with Cloud Build

For automated deployments, you can use Google Cloud Build:

```bash
# Trigger a build manually
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_REGION=us-central1

# Or set up automated builds from GitHub
# (requires connecting your repository to Cloud Build)
```

## Configuration

### Environment Variables

#### Backend
- `PORT`: Port to run on (default: 8080, set by Cloud Run)
- `PYTHONUNBUFFERED`: Ensures logs are displayed (set to 1)

#### Frontend
- `ADK_API_URL`: URL of the backend API (automatically set during deployment)
- `PORT`: Port to run on (default: 8080, set by Cloud Run)
- `PYTHONUNBUFFERED`: Ensures logs are displayed (set to 1)

### Resource Allocation

Current configuration (can be modified in deployment scripts):
- **Memory**: 1GB
- **CPU**: 1 vCPU
- **Timeout**: 300 seconds
- **Max Instances**: 10
- **Min Instances**: 0 (scales to zero when not in use)

## Post-Deployment

### Testing the Deployment

1. **Test Backend Health**:
   ```bash
   # Get the backend URL
   BACKEND_URL=$(gcloud run services describe slimpai-backend \
     --region $GCP_REGION \
     --format 'value(status.url)')
   
   # Test the health endpoint
   curl $BACKEND_URL/health
   ```

2. **Access the Frontend**:
   ```bash
   # Get the frontend URL
   FRONTEND_URL=$(gcloud run services describe slimpai-frontend \
     --region $GCP_REGION \
     --format 'value(status.url)')
   
   echo "Open in browser: $FRONTEND_URL"
   ```

### Viewing Logs

```bash
# Backend logs
gcloud run logs read slimpai-backend --region $GCP_REGION

# Frontend logs
gcloud run logs read slimpai-frontend --region $GCP_REGION

# Follow logs in real-time
gcloud run logs tail slimpai-backend --region $GCP_REGION
gcloud run logs tail slimpai-frontend --region $GCP_REGION
```

### Updating the Application

To deploy updates:

```bash
# Re-run the deployment scripts
./deploy-all.sh

# Or deploy services individually
./deploy-backend.sh
./deploy-frontend.sh
```

## Cost Optimization

Cloud Run pricing is based on:
- **CPU and memory usage** (per 100ms)
- **Requests**
- **Egress traffic**

Tips to reduce costs:
1. The configuration uses `min-instances=0` to scale to zero when idle
2. Consider reducing memory/CPU if the app doesn't need 1GB/1vCPU
3. Use Cloud Run's free tier: 2 million requests/month, 360,000 GB-seconds memory

## Troubleshooting

### Build Failures

```bash
# Check Cloud Build logs
gcloud builds list --limit=5

# View specific build
gcloud builds log <BUILD_ID>
```

### Service Not Starting

```bash
# Check service status
gcloud run services describe slimpai-backend --region $GCP_REGION

# View recent logs
gcloud run logs read slimpai-backend --region $GCP_REGION --limit=50
```

### Connection Issues

If frontend can't connect to backend:
1. Verify backend URL is correct in frontend environment
2. Check that backend is allowing unauthenticated requests
3. Verify both services are in the same region (recommended)

## Security Considerations

### Current Setup (Development)
- Services are publicly accessible (`--allow-unauthenticated`)
- No authentication required

### Production Recommendations
1. **Add Authentication**: 
   - Remove `--allow-unauthenticated`
   - Implement Cloud IAM authentication
   - Add user authentication (Firebase Auth, etc.)

2. **Use HTTPS**: Cloud Run provides HTTPS by default

3. **Secret Management**:
   - Use Google Secret Manager for API keys
   - Don't commit secrets to repository

4. **Network Security**:
   - Consider VPC connector for private services
   - Implement rate limiting
   - Add CORS configuration

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Best Practices for Cloud Run](https://cloud.google.com/run/docs/tips)
- [Pricing Calculator](https://cloud.google.com/products/calculator)

## Support

For issues specific to this deployment:
1. Check the logs using the commands above
2. Verify all environment variables are set correctly
3. Ensure your GCP project has billing enabled
4. Check that all required APIs are enabled
