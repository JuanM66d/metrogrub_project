# MetroGrub Model Pipeline Cloud Function

This directory contains a Cloud Function that automatically triggers the MetroGrub ML pipeline on a quarterly schedule using Cloud Scheduler.

## Overview

The model pipeline cloud function provides a serverless way to automatically run your Vertex AI ML pipeline. It integrates with the existing pipeline_v3 system and is scheduled to run quarterly, one hour after your data cleaning and master table creation processes complete.

## Files

### Test Mode Files (Safe for Development)
- **`main.py`** - Currently the active cloud function code (switches between test/production)
- **`deploy.sh`** - Deploys in test mode (safe, no real pipelines created)

### Production Mode Files (Real Pipeline Execution)
- **`main_production.py`** - Production version that triggers real Vertex AI pipelines
- **`deploy_production.sh`** - Deploys in production mode (creates real pipeline jobs)

### Shared Files (Used in Both Modes)
- **`requirements.txt`** - Python package dependencies
- **`manage.py`** - Management utilities for testing, monitoring, and troubleshooting
- **`README.md`** - This documentation

## How It Works

The system operates in two modes:

**Test Mode** (default): Safe for development and testing. Uses `main.py` and `deploy.sh`. The function executes successfully but doesn't create actual pipeline jobs.

**Production Mode**: Uses `main_production.py` and `deploy_production.sh`. Triggers real Vertex AI pipeline jobs that process your data and train ML models.

The cloud function runs quarterly on the 1st of January, April, July, and October at 7 AM Chicago time, which is perfectly timed to run one hour after your master table creation completes.

## Configuration

The function is configured through environment variables that are automatically set during deployment:

### Core Settings
- `PROJECT_ID` - Your Google Cloud project ID
- `LOCATION` - Vertex AI region (us-central1)
- `SERVICE_ACCOUNT` - Service account used to run pipelines
- `TEMPLATE_PATH` - Location of the compiled pipeline template (only set in production mode)

### Optional Overrides
- `TARGET_TABLE` - Override the default target table for predictions
- `SOURCE_TABLE` - Override the default source table for training data
- `PREDICTION_COLUMN` - Override the default prediction column name
- `ENABLE_CACHING` - Enable pipeline caching (default: disabled)

## Deployment

### Prerequisites

Before deploying, make sure you have:
- Google Cloud CLI installed and authenticated (`gcloud auth login`)
- Required APIs enabled (Cloud Functions, Cloud Scheduler, App Engine, Vertex AI)

### Test Mode Deployment (Safe - Recommended for Development)

For safe testing and development, use the test mode files:

```bash
cd cloud_functions/model_pipeline
./deploy.sh
```

This uses `main.py` and deploys in test mode where it runs successfully but doesn't create real pipeline jobs.

### Production Mode Deployment (Real Pipelines - Use with Caution)

For real pipeline execution, switch to production mode files:

```bash
cd cloud_functions/model_pipeline
./deploy_production.sh
```

This switches to `main_production.py` and deploys with a real pipeline template that will create actual Vertex AI jobs that cost money and process real data.

### Manual Deployment

If you prefer to deploy components individually:

#### Deploy Cloud Function
```bash
gcloud functions deploy metrogrub-model-pipeline \
    --gen2 \
    --runtime=python311 \
    --region=us-central1 \
    --source=. \
    --entry-point=trigger_model_pipeline \
    --trigger-http \
    --timeout=540s \
    --memory=512MB \
    --service-account=119856114569-compute@developer.gserviceaccount.com
```

#### Create Scheduler Job
```bash
gcloud scheduler jobs create http metrogrub-pipeline-scheduler \
    --location=us-central1 \
    --schedule="0 2 * * *" \
    --uri="[FUNCTION_URL]" \
    --http-method=POST \
    --oidc-service-account-email=119856114569-compute@developer.gserviceaccount.com
```

## Usage

### Automatic Execution
The scheduler automatically triggers the pipeline quarterly on the 1st of January, April, July, and October at 7 AM Chicago time.

### Manual Testing
Use the management script for easy testing and monitoring:

```bash
# Test the function
python3 manage.py trigger

# Check status
python3 manage.py status

# View logs
python3 manage.py logs

# Monitor pipeline activity
python3 manage.py monitor

# See all available commands
python3 manage.py help
```

### Direct Commands
You can also use gcloud commands directly:

```bash
# Trigger scheduler manually
gcloud scheduler jobs run metrogrub-pipeline-scheduler --location=us-central1

# View function logs
gcloud functions logs read metrogrub-model-pipeline --region=us-central1
```

## Understanding the Output

### Test Mode Response
In test mode, the function returns a simple success message confirming it ran without creating actual pipelines.

### Production Mode Response
In production mode, the function submits a real pipeline job to Vertex AI and returns details including the job name and console URL for monitoring.

Note: You may see a "PipelineJob resource has not been created" error in the logs, but this is normal. The pipeline job is actually created successfully - there's just a small delay before it becomes queryable.

## Customization

### Changing the Schedule
The quarterly schedule is defined in the deployment scripts. To modify it, edit the `SCHEDULE_CRON` variable:

```bash
# Current: Quarterly on 1st at 7 AM Chicago time
SCHEDULE_CRON="0 7 1 1,4,7,10 *"

# Examples of other schedules:
SCHEDULE_CRON="0 2 * * *"      # Daily at 2 AM
SCHEDULE_CRON="0 */6 * * *"    # Every 6 hours
SCHEDULE_CRON="0 0 * * 0"      # Weekly on Sundays
```

### Adding Pipeline Parameters
To override default pipeline parameters, edit the deployment scripts and uncomment the parameter lines:

```bash
ENV_VARS="${ENV_VARS},TARGET_TABLE=your.project.predictions"
ENV_VARS="${ENV_VARS},SOURCE_TABLE=your.project.training_data"
```

## Troubleshooting

### Common Issues

**Function not triggering**: Check that App Engine is enabled in your project (required for Cloud Scheduler).

**Permission errors**: Verify the service account has the required IAM roles:
- `roles/aiplatform.user` - Submit Vertex AI pipeline jobs
- `roles/storage.admin` - Access GCS buckets  
- `roles/bigquery.dataEditor` - Read/write BigQuery data

**Template not found**: In production mode, ensure your pipeline template exists at the specified GCS path.

**"PipelineJob resource has not been created" error**: This is normal and expected. The pipeline job is actually created successfully despite this message.

### Debugging

Check function execution logs:
```bash
python3 manage.py logs
```

Verify scheduler configuration:
```bash
python3 manage.py status
```

Test the function manually:
```bash
python3 manage.py trigger
```

## Integration with pipeline_v3

This cloud function integrates directly with your existing ML pipeline system. It uses the same configuration and APIs as the pipeline_v3 directory, just triggered automatically on a schedule instead of manually.

The function loads your compiled pipeline template from GCS and submits it to Vertex AI with any parameter overrides you've configured. 