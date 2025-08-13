#!/bin/bash

# Production deployment script for testing real pipeline deployment
# This deploys the cloud function with the TEMPLATE_PATH set to trigger real pipelines

set -e  # Exit on any error

# Configuration
PROJECT_ID="purple-25-gradient-20250605"
REGION="us-central1"
FUNCTION_NAME="metrogrub-model-pipeline"
SCHEDULER_JOB_NAME="metrogrub-pipeline-scheduler"
SERVICE_ACCOUNT="119856114569-compute@developer.gserviceaccount.com"
TEMPLATE_PATH="gs://purple-25-gradient-20250605-vertex-ai-pipelines/templates/metrogrub_pipeline_v3.json"

# Environment variables for PRODUCTION mode (with real pipeline)
ENV_VARS="PROJECT_ID=${PROJECT_ID}"
ENV_VARS="${ENV_VARS},LOCATION=${REGION}"
ENV_VARS="${ENV_VARS},PIPELINE_ROOT=gs://${PROJECT_ID}-vertex-ai-pipelines/pipeline_root"
ENV_VARS="${ENV_VARS},SERVICE_ACCOUNT=${SERVICE_ACCOUNT}"
ENV_VARS="${ENV_VARS},TEMPLATE_PATH=${TEMPLATE_PATH}"
ENV_VARS="${ENV_VARS},CONFIG_BUCKET=${PROJECT_ID}-vertex-ai-pipelines"
ENV_VARS="${ENV_VARS},ENABLE_CACHING=false"

# Optional: Add table overrides for testing
# ENV_VARS="${ENV_VARS},TARGET_TABLE=${PROJECT_ID}.metrogrub_production.predictions"
# ENV_VARS="${ENV_VARS},SOURCE_TABLE=${PROJECT_ID}.metrogrub_master.master_table"
# ENV_VARS="${ENV_VARS},PREDICTION_COLUMN=foot_traffic_prediction"

echo "🚀 Deploying MetroGrub Model Pipeline in PRODUCTION MODE..."
echo "Project: ${PROJECT_ID}"
echo "Template: ${TEMPLATE_PATH}"
echo "Mode: REAL PIPELINE DEPLOYMENT"
echo ""

# Backup current main.py and switch to production version
echo "📝 Switching to production version..."
if [ -f "main.py" ]; then
    cp main.py main_test.py
    echo "✅ Backed up test version to main_test.py"
fi

cp main_production.py main.py
echo "✅ Switched to production version"

# Deploy the Cloud Function in production mode
echo "☁️ Deploying Cloud Function in PRODUCTION MODE..."
gcloud functions deploy ${FUNCTION_NAME} \
    --gen2 \
    --runtime=python311 \
    --region=${REGION} \
    --source=. \
    --entry-point=trigger_model_pipeline \
    --trigger-http \
    --timeout=540s \
    --memory=512MB \
    --service-account=${SERVICE_ACCOUNT} \
    --set-env-vars="${ENV_VARS}" \
    --no-allow-unauthenticated \
    --max-instances=1

echo "✅ Production Cloud Function deployed successfully!"

# Get the function URL
FUNCTION_URL=$(gcloud functions describe ${FUNCTION_NAME} --region=${REGION} --format="value(serviceConfig.uri)")
echo "🔗 Function URL: ${FUNCTION_URL}"

echo ""
echo "📊 Production Deployment Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Function: ${FUNCTION_NAME} (PRODUCTION MODE)"
echo "✅ Template: ${TEMPLATE_PATH}"
echo "✅ Mode: REAL PIPELINE DEPLOYMENT"
echo "✅ Region: ${REGION}"
echo ""

echo "🧪 How to Test Real Pipeline Deployment:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 🔥 Trigger real pipeline deployment:"
echo "   python3 manage.py trigger"
echo ""
echo "2. 📝 Check execution logs:"
echo "   python3 manage.py logs"
echo ""
echo "3. 📊 Monitor in Vertex AI Console:"
echo "   https://console.cloud.google.com/vertex-ai/pipelines?project=${PROJECT_ID}"
echo ""
echo "4. 🔍 Check function status:"
echo "   python3 manage.py status"
echo ""

echo "⚠️  IMPORTANT NOTES:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "• This will trigger REAL Vertex AI pipeline jobs"
echo "• Jobs will consume compute resources and may incur costs"
echo "• Pipeline will process actual data from your master table"
echo "• To switch back to test mode, run: ./deploy.sh"
echo ""
echo "🎉 Ready to test real pipeline deployment!" 