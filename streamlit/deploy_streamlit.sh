#!/bin/bash
set -e

PROJECT_ID="purple-25-gradient-20250605"  # Hardcoded from terraform.tfvars
REGION="us-central1"
IMAGE_NAME="streamlit-app"
FULL_IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${IMAGE_NAME}/${IMAGE_NAME}:latest"

echo "🚀 Deploying MetroGrub Streamlit App..."

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "📄 Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
else
    echo "⚠️  No .env file found. Make sure environment variables are set manually."
fi

# Check if required environment variables are set
if [ -z "$LOOKER_CLIENT_ID" ]; then
    echo "❌ Error: LOOKER_CLIENT_ID environment variable is not set"
    exit 1
fi

if [ -z "$LOOKER_CLIENT_SECRET" ]; then
    echo "❌ Error: LOOKER_CLIENT_SECRET environment variable is not set"
    exit 1
fi

echo "✅ Environment variables validated"

# Docker
docker build --no-cache --platform linux/amd64 -t "$IMAGE_NAME:latest" . && cd ..
docker tag "$IMAGE_NAME:latest" "$FULL_IMAGE_NAME"
docker push "$FULL_IMAGE_NAME"

echo "Docker build complete"

# Deploy with environment variables
gcloud run deploy metrogrub-streamlit-app \
  --image="$FULL_IMAGE_NAME" \
  --region="$REGION" \
  --allow-unauthenticated \
  --set-env-vars="LOOKER_CLIENT_ID=${LOOKER_CLIENT_ID},LOOKER_CLIENT_SECRET=${LOOKER_CLIENT_SECRET}" 

echo "✅ Done! Check: gcloud run services list" 