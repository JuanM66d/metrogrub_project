#!/bin/bash
set -e

PROJECT_ID="purple-25-gradient-20250605"  # Hardcoded from terraform.tfvars
REGION="us-central1"
IMAGE_NAME="streamlit-app"
FULL_IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${IMAGE_NAME}/${IMAGE_NAME}:latest"

echo "🚀 Deploying MetroGrub Streamlit App..."

# Infrastructure
cd infra && terraform apply -auto-approve && cd ..

# Docker
cd streamlit && docker build -t "$IMAGE_NAME:latest" . && cd ..
docker tag "$IMAGE_NAME:latest" "$FULL_IMAGE_NAME"
docker push "$FULL_IMAGE_NAME"

# Deploy
gcloud run deploy metrogrub-streamlit-app --image="$FULL_IMAGE_NAME" --region="$REGION" --allow-unauthenticated

echo "✅ Done! Check: gcloud run services list" 