#!/bin/bash

# MetroGrub Model Pipeline Cloud Function and Scheduler Deployment Script
# This script deploys the cloud function and sets up a Cloud Scheduler job

set -e  # Exit on any error

# Configuration
PROJECT_ID="purple-25-gradient-20250605"
REGION="us-central1"
FUNCTION_NAME="metrogrub-model-pipeline"
SCHEDULER_JOB_NAME="metrogrub-pipeline-scheduler"
SCHEDULE_CRON="0 7 1 1,4,7,10 *"  # Quarterly on 1st at 7 AM Chicago time (1 hour after master table creation at 6 AM)
TIMEOUT="540s"  # 9 minutes (Cloud Functions max is 9 minutes)
MEMORY="512MB"
SERVICE_ACCOUNT="119856114569-compute@developer.gserviceaccount.com"

# Environment variables for the cloud function
ENV_VARS="PROJECT_ID=${PROJECT_ID}"
ENV_VARS="${ENV_VARS},LOCATION=${REGION}"
ENV_VARS="${ENV_VARS},PIPELINE_ROOT=gs://${PROJECT_ID}-vertex-ai-pipelines/pipeline_root"
ENV_VARS="${ENV_VARS},SERVICE_ACCOUNT=${SERVICE_ACCOUNT}"
# ENV_VARS="${ENV_VARS},TEMPLATE_PATH=gs://${PROJECT_ID}-vertex-ai-pipelines/templates/metrogrub_pipeline_v3.yaml"
ENV_VARS="${ENV_VARS},CONFIG_BUCKET=${PROJECT_ID}-vertex-ai-pipelines"
ENV_VARS="${ENV_VARS},ENABLE_CACHING=false"

# Optional: Add table overrides (uncomment and modify as needed)
# ENV_VARS="${ENV_VARS},TARGET_TABLE=purple-25-gradient-20250605.metrogrub_production.predictions"
# ENV_VARS="${ENV_VARS},SOURCE_TABLE=purple-25-gradient-20250605.metrogrub_master.master_table"
# ENV_VARS="${ENV_VARS},PREDICTION_COLUMN=foot_traffic_prediction"

echo "🚀 Deploying MetroGrub Model Pipeline Cloud Function..."
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Function: ${FUNCTION_NAME}"
echo "Schedule: ${SCHEDULE_CRON}"
echo ""

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Error: No active gcloud authentication found."
    echo "Please run: gcloud auth login"
    exit 1
fi

# Set the project
echo "📝 Setting project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable appengine.googleapis.com  # Required for Cloud Scheduler
gcloud services enable aiplatform.googleapis.com

# Deploy the Cloud Function
echo "☁️ Deploying Cloud Function..."
gcloud functions deploy ${FUNCTION_NAME} \
    --gen2 \
    --runtime=python311 \
    --region=${REGION} \
    --source=. \
    --entry-point=trigger_model_pipeline \
    --trigger-http \
    --timeout=${TIMEOUT} \
    --memory=${MEMORY} \
    --service-account=${SERVICE_ACCOUNT} \
    --set-env-vars="${ENV_VARS}" \
    --no-allow-unauthenticated \
    --max-instances=1

echo "✅ Cloud Function deployed successfully!"

# Get the function URL
FUNCTION_URL=$(gcloud functions describe ${FUNCTION_NAME} --region=${REGION} --format="value(serviceConfig.uri)")
echo "🔗 Function URL: ${FUNCTION_URL}"

# Create or update Cloud Scheduler job
echo "⏰ Setting up Cloud Scheduler job..."

# Check if scheduler job exists
if gcloud scheduler jobs describe ${SCHEDULER_JOB_NAME} --location=${REGION} >/dev/null 2>&1; then
    echo "📝 Updating existing scheduler job..."
    gcloud scheduler jobs update http ${SCHEDULER_JOB_NAME} \
        --location=${REGION} \
        --schedule="${SCHEDULE_CRON}" \
        --uri="${FUNCTION_URL}" \
        --http-method=POST \
        --oidc-service-account-email=${SERVICE_ACCOUNT} \
        --headers="Content-Type=application/json" \
        --message-body='{"trigger":"scheduler"}' \
        --time-zone="America/Chicago"
else
    echo "🆕 Creating new scheduler job..."
    gcloud scheduler jobs create http ${SCHEDULER_JOB_NAME} \
        --location=${REGION} \
        --schedule="${SCHEDULE_CRON}" \
        --uri="${FUNCTION_URL}" \
        --http-method=POST \
        --oidc-service-account-email=${SERVICE_ACCOUNT} \
        --headers="Content-Type=application/json" \
        --message-body='{"trigger":"scheduler"}' \
        --time-zone="America/Chicago"
fi

echo "✅ Cloud Scheduler job configured successfully!"

# Test the function (optional)
echo ""
echo "🧪 Testing the function..."
echo "You can test the function manually with:"
echo "gcloud functions call ${FUNCTION_NAME} --region=${REGION} --data='{\"test\":true}'"
echo ""

# Manual trigger command
echo "⚡ To manually trigger the scheduler job:"
echo "gcloud scheduler jobs run ${SCHEDULER_JOB_NAME} --location=${REGION}"
echo ""

# Show status
echo "📊 Deployment Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Cloud Function: ${FUNCTION_NAME}"
echo "✅ Scheduler Job: ${SCHEDULER_JOB_NAME}"
echo "✅ Schedule: ${SCHEDULE_CRON} (Quarterly on 1st at 7 AM Chicago time)"
echo "✅ Region: ${REGION}"
echo "✅ Function URL: ${FUNCTION_URL}"
echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Monitor function logs: gcloud functions logs read ${FUNCTION_NAME} --region=${REGION}"
echo "2. View scheduler jobs: gcloud scheduler jobs list --location=${REGION}"
echo "3. Check Vertex AI pipelines: https://console.cloud.google.com/vertex-ai/pipelines"
echo "" 