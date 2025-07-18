#!/bin/bash
set -e

PROJECT_ID="purple-25-gradient-20250605"  # Hardcoded from terraform.tfvars
REGION="us-central1"
IMAGE_NAME="streamlit-app"
FULL_IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${IMAGE_NAME}/${IMAGE_NAME}:latest"

echo "🚀 Deploying MetroGrub Streamlit App..."

# Docker
docker build --no-cache --platform linux/amd64 -t "$IMAGE_NAME:latest" . && cd ..
docker tag "$IMAGE_NAME:latest" "$FULL_IMAGE_NAME"
docker push "$FULL_IMAGE_NAME"

echo "Docker build complete"

# Deploy
gcloud run deploy metrogrub-streamlit-app --image="$FULL_IMAGE_NAME" --region="$REGION" --allow-unauthenticated

echo "✅ Done! Check: gcloud run services list" 